from deform import widget
import colander
from ..models import GroupPermission
from . import BaseViews
from ..i18n import _
from ..models import Group

class ListSchema(colander.Schema):
    group_id = colander.SchemaNode(colander.Set(),
                                   title="Group",
                                   widget=widget.CheckboxChoiceWidget(values=[]),)
    perm_name = colander.SchemaNode(colander.String())

    def after_bind(self, schema, appstruct):

        groups = Group.query().all()
        schema['group_id'].widget.values = [
            (str(g.id), g.group_name) for g in groups
        ]
class CreateSchema(ListSchema):
    pass
class UpdateSchema(ListSchema):
    pass    
  


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = GroupPermission
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema  
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = 'group-permission-list'

    
