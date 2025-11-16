from pyramid.security import Allow, Authenticated, ALL_PERMISSIONS
import sqlalchemy as sa
from sqlalchemy.orm import relationship
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
from datetime import timezone
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import (
    DateTime,
    Column,
    Integer
)
class User(UserMixin, DefaultModel, Base):
    updated = Column(DateTime)
    last_login_date = sa.Column(
            sa.TIMESTAMP(timezone=True),
            default=lambda x: datetime.now(timezone.utc),
            server_default=sa.func.now(),
        )
    security_code_date = sa.Column(
            sa.TIMESTAMP(timezone=True),
            default=datetime(2000, 1, 1),
            server_default="2000-01-01 01:01",
        )

    @classmethod
    def get_by_identity(cls, identity):
        return DBSession.query(cls).filter(
            sa.or_(cls.user_name == identity,
                   cls.email == identity)).first()

    @property
    def nice_username(self):
        if self.user_name and self.user_name.strip():
            return self.user_name
        return self.email
    
    external = sa.orm.relationship("ExternalIdentity",
                            backref="user",)
    
    order_created = relationship('Order', foreign_keys="[Order.created_uid]", back_populates='user_created')
    order_updated = relationship('Order', foreign_keys="[Order.updated_uid]", back_populates='user_updated')

    provinsi_created = relationship('Provinsi', foreign_keys="[Provinsi.created_uid]", back_populates='user_created')
    provinsi_updated = relationship('Provinsi', foreign_keys="[Provinsi.updated_uid]", back_populates='user_updated')

    products_created = relationship('Product', foreign_keys="[Product.created_uid]", back_populates='user_created')
    products_updated = relationship('Product', foreign_keys="[Product.updated_uid]", back_populates='user_updated')

    kota_created = relationship('Kota', foreign_keys="[Kota.created_uid]", back_populates='user_created')
    kota_updated = relationship('Kota', foreign_keys="[Kota.updated_uid]", back_populates='user_updated')

    kecamatan_created = relationship('Kecamatan', foreign_keys="[Kecamatan.created_uid]", back_populates='user_created')
    kecamatan_updated = relationship('Kecamatan', foreign_keys="[Kecamatan.updated_uid]", back_populates='user_updated')

    partner_created = relationship('Partner', foreign_keys="[Partner.created_uid]", back_populates='user_created')
    partner_updated = relationship('Partner', foreign_keys="[Partner.updated_uid]", back_populates='user_updated')



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
