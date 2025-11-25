from deform import widget
import colander
import deform
import re
from ..models import Group
from . import BaseViews
from ..i18n import _
from ..models import Permissions
class ListSchema(colander.Schema):    
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             title="Action",
                             widget = widget.HiddenWidget())
    group_name = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String())

class CreateSchema(colander.Schema):    
    # Define your schema fields here
    group_name = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String())
    perm_names = colander.SchemaNode(
        colander.Set(),
        title =_("Permissions"),
        widget = widget.CheckboxChoiceWidget(values=[]), 
    )

    def after_bind_perm(self, schema_class):
    #     # Populate perm_names choices
        permissions = Permissions.query().all()
        schema_class['perm_names'].widget.values = [
            (str(p.name), p.description) for p in permissions
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
        

    

