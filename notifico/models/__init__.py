# -*- coding: utf8 -*-
__all__ = (
    'known_models',
)
from sqlalchemy import func
from sqlalchemy.ext.hybrid import Comparator


class CaseInsensitiveComparator(Comparator):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)

# NOTE: All of our models need to be imported if they
#       use relationships. Otherwise, SQLAlchemy may
#       not see the backref and wont' set the model
#       properities.
from notifico.models.user import UserModel, GroupModel
from notifico.models.channel import ChannelModel
from notifico.models.hook import HookModel
from notifico.models.project import ProjectModel
from notifico.models.token import AuthTokenModel

known_models = [
    UserModel,
    GroupModel,
    ChannelModel,
    HookModel,
    ProjectModel,
    AuthTokenModel
]
