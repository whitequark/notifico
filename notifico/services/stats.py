# -*- coding: utf-8 -*-
"""
A collection of utility methods for common site statistics.
"""
from sqlalchemy import func

from notifico.server import db, cache
from notifico.models import ProjectModel, ChannelModel, UserModel


@cache.memoize(timeout=60 * 5)
def total_messages(user=None):
    """
    Sum the total number of messages across all projects.
    """
    q = db.session.query(
        func.sum(ProjectModel.message_count)
    )
    if user:
        q = q.filter(ProjectModel.owner_id == user.id)

    return q.scalar() or 0


@cache.memoize(timeout=60 * 5)
def total_users():
    return UserModel.query.count()


@cache.memoize(timeout=60 * 5)
def total_projects():
    return ProjectModel.query.count()


@cache.memoize(timeout=60 * 5)
def total_networks():
    return db.session.query(
        func.count(func.distinct(ChannelModel.host)).label('count')
    ).scalar()


@cache.memoize(timeout=60 * 5)
def top_networks(limit=20):
    return (
        db.session.query(
            ChannelModel.host,
            func.count(func.distinct(ChannelModel.channel)).label('count'),
        )
        .join(ChannelModel.project).filter(
            ProjectModel.public == True,
            ChannelModel.public == True
        )
        .group_by(ChannelModel.host)
        .order_by('count desc')
        .limit(limit)
    ).all()
