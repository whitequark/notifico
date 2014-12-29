# -*- coding: utf-8 -*-
from flask import (
    Blueprint,
    render_template,
    request
)
from flask.ext.login import current_user
from flask.ext.sqlalchemy import Pagination
from sqlalchemy import func

from notifico.server import db
from notifico.services import stats
from notifico.models import UserModel, ChannelModel, ProjectModel
from notifico.services.hooks import HookService

public = Blueprint('public', __name__, template_folder='templates')


@public.route('/')
def landing():
    return render_template(
        'landing.html',
        new_projects=[],
        top_networks=stats.top_networks(limit=10),
        total_networks=stats.total_networks(),
        total_users=stats.total_users()
    )


@public.route('/s/networks/')
def networks():
    per_page = min(int(request.args.get('l', 25)), 100)
    page = max(int(request.args.get('page', 1)), 1)

    q = (
        ChannelModel.visible(db.session.query(
            ChannelModel.host,
            func.count(func.distinct(ChannelModel.channel)).label('di_count'),
            func.count(ChannelModel.channel).label('count')
        ), user=current_user)
        .group_by(ChannelModel.host)
        .order_by('di_count desc')
    )
    total = q.count()
    items = q.limit(per_page).offset((page - 1) * per_page).all()
    pagination = Pagination(q, page, per_page, total, items)

    return render_template(
        'networks.html',
        pagination=pagination,
        per_page=per_page
    )


@public.route('/s/networks/<network>/')
def network(network):
    per_page = min(int(request.args.get('l', 25)), 100)
    page = max(int(request.args.get('page', 1)), 1)

    q = ChannelModel.visible(
        ChannelModel.query.filter(ChannelModel.host == network),
        user=current_user
    ).order_by(ChannelModel.created.desc())

    pagination = q.paginate(page, per_page, False)

    return render_template(
        'channels.html',
        per_page=per_page,
        network=network,
        pagination=pagination
    )


@public.route('/s/projects', defaults={'page': 1})
@public.route('/s/projects/<int:page>')
def projects(page=1):
    per_page = min(int(request.args.get('l', 25)), 100)
    sort_by = request.args.get('s', 'created')

    q = ProjectModel.visible(
        ProjectModel.query,
        user=current_user
    ).order_by(False)
    q = q.order_by({
        'created': ProjectModel.created.desc(),
        'messages': ProjectModel.message_count.desc()
    }.get(sort_by, ProjectModel.created.desc()))

    pagination = q.paginate(page, per_page, False)

    return render_template(
        'projects.html',
        pagination=pagination,
        per_page=per_page
    )


@public.route('/s/users', defaults={'page': 1})
@public.route('/s/users/<int:page>')
def users(page=1):
    per_page = min(int(request.args.get('l', 25)), 100)
    sort_by = request.args.get('s', 'created')

    q = UserModel.query.order_by(False)
    q = q.order_by({
        'created': UserModel.joined.desc()
    }.get(sort_by, UserModel.joined.desc()))

    pagination = q.paginate(page, per_page, False)

    return render_template(
        'users.html',
        pagination=pagination,
        per_page=per_page
    )


@public.route('/s/services')
def services():
    services = HookService.services
    return render_template(
        'services.html',
        services=services
    )
