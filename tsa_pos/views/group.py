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
    

    def after_save(self, row, values):
    # BAGIAN GROUP (sudah benar)
        permissions = set(values.get('perm_names', []))
        existing = set()
        q = GroupPermission.query().filter(GroupPermission.group_id == row.id)
        for gp in q:
            existing.add(str(gp.perm_name))

        delete_ids = existing - permissions
        for perm_name in delete_ids:
            q = GroupPermission.query().filter(
                GroupPermission.group_id == row.id,
                GroupPermission.perm_name == str(perm_name)
            )
            gp = q.first()
            if gp:
                self.db_session.delete(gp)
                self.db_session.flush()
        
        new_ids = permissions - existing
        for perm_name in new_ids:
            new_gp = GroupPermission(
                group_id=row.id,
                perm_name=str(perm_name)
            )
            self.db_session.add(new_gp)
            self.db_session.flush()

        # BAGIAN PERMISSIONS (tambahkan ini!!)

        return row




    

