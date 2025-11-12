from pyramid.security import Allow, Authenticated, ALL_PERMISSIONS
import sqlalchemy as sa
from ziggurat_foundations.models.user    import UserMixin
from ziggurat_foundations.models.group  import GroupMixin
from ziggurat_foundations.models.user_group import UserGroupMixin
from ziggurat_foundations.models.user_permission import UserPermissionMixin
from ziggurat_foundations.models.user_resource_permission import \
    UserResourcePermissionMixin
from ziggurat_foundations.models.group_resource_permission import \
    GroupResourcePermissionMixin
from ziggurat_foundations.models.resource import ResourceMixin
from ziggurat_foundations.models.external_identity import ExternalIdentityMixin
from ziggurat_foundations.models.group_permission import GroupPermissionMixin
from ziggurat_foundations.models.services.user import UserService
from ziggurat_foundations import ziggurat_model_init
from .base import DefaultModel
from .meta import Base
from .import DBSession


class User(UserMixin, DefaultModel, Base):
    pass


class Group(GroupMixin, DefaultModel, Base):
    pass

class GroupPermission(GroupPermissionMixin, DefaultModel, Base):
    pass


class UserGroup(UserGroupMixin, Base):
    pass


class UserPermission(UserPermissionMixin, Base):
    pass


class UserResourcePermission(UserResourcePermissionMixin,
                              Base):
    pass


class GroupResourcePermission(GroupResourcePermissionMixin,
                               Base):
    pass


class Resource(ResourceMixin, Base):
    pass


class ExternalIdentity(ExternalIdentityMixin, Base):
    pass


class RootFactory:
    def __init__(self, request):
        gr = DBSession.query(Group).filter_by(group_name="Superuser").first()
        gr_id = gr and gr.id or 1
        self.__acl__ = [
            (Allow, f'group:{gr_id}', ALL_PERMISSIONS),
            (Allow, Authenticated, 'view')]
        for gp in DBSession.query(GroupPermission):
            acl_name = 'group:{}'.format(gp.group_id)
            self.__acl__.append((Allow, acl_name, gp.perm_name))


def init_model():
    ziggurat_model_init(User, Group, UserGroup, GroupPermission, UserPermission,
                        UserResourcePermission, GroupResourcePermission,
                        Resource,
                        ExternalIdentity, passwordmanager=None)
