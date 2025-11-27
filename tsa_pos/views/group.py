from deform import widget
import colander
import deform
import re
from ..models import Group
from . import BaseViews
from ..i18n import _
from ..models import Permissions
from ..models import GroupPermission
from sqlalchemy.orm import Session
class ListSchema(colander.Schema):    
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             title="Action",
                             widget = widget.HiddenWidget())
    group_name = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String())

class CreateSchema(colander.Schema):
    group_name = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String())

    perm_names = colander.SchemaNode(
        colander.Set(),
        title=_("Permissions"),
        widget=widget.CheckboxChoiceWidget(values=[]),
    )

    def after_bind(self, node, kw):
        permissions = Permissions.query().all()

        node['perm_names'].widget.values = [
            (p.name, p.description) for p in permissions
        ]

class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             widget = widget.HiddenWidget())
   

# def save_group_permissions(group, perm_names, dbsession: Session):
#     group.group_permissions.clear()

#         # Tambahkan permission baru
#     for perm in perm_names:
#         gp = GroupPermission(
#             group_id=group.id,
#             perm_name=perm.lower()   # penting: lowercase
#         )
#         group.group_permissions.append(gp)

#         dbsession.flush()
class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Group  # Assuming User is your SQLAlchemy model
        self.CreateSchema = CreateSchema
        self.UpdateSchema = CreateSchema  # For simplicity, using the same schema
        self.ReadSchema = CreateSchema  # For simplicity, using the same schema
        self.ListSchema = ListSchema
        self.list_route = 'group-list'

    def form_validator(self, form, value):
        id_ = self.request.matchdict.get('id', 0)
        group_name = value.get('group_name')
        exc = colander.Invalid(
            form,
            'Kesalahan pada pengisian data.'
        )
        row = Group.query().filter(
            Group.group_name == group_name
        ).first()
        if row and (not id_ or row.id != int(id_)):
            exc["group_name"] = _('Group Name {} already exists.'.format(group_name))
            raise exc
        
    def get_values(self, row):
        values = super().get_values(row)
        q = GroupPermission.query().filter(GroupPermission.group_id == row.id)
        permissions = [str(perm.perm_name) for perm in q]
        values['perm_names'] = set(permissions)
        return values
    
    # def save(self, values, row=None):
    #     row = super().save(values, row)

    #     perm_names = values.get("perm_names", [])
    #     save_group_permissions(row, perm_names, self.db_session)

    #     return row
    
    # def before_update(self, form, row):
    # # Ambil perm lama
    #     selected = {gp.perm_name for gp in row.group_permissions}

    #     # Set default value ke form
    #     form.appstruct['perm_names'] = selected



    

