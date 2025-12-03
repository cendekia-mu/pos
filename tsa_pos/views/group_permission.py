from deform import widget
import colander
from ..models import GroupPermission
from . import BaseViews
from ..i18n import _
from ..models import Group
from pyramid.httpexceptions import HTTPFound

class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Set(),
                                   title="Group",
                                   field=Group.id)
    group_name = colander.SchemaNode(colander.String(),
                                    title=_("Group Name"),
                                    field=Group.group_name)
    perm_name = colander.SchemaNode(colander.String())

    # def after_bind(self, schema, appstruct):

    #     groups = Group.query().all()
    #     schema['group_id'].widget.values = [
    #         (str(g.id), g.group_name) for g in groups
    #     ]
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
        self.allow_add = False
    
        self.allow_delete = False
        self.allow_view = False

    def list_join(self, query):
        return query.join(Group, Group.id == GroupPermission.group_id)
    
    def view_edit(self):
        return HTTPFound(location=self.request.route_url('group-edit', id=self.request.matchdict['id']))
      
    

    
