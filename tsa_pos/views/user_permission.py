from deform import widget
import colander
from ..models import UserPermission
from . import BaseViews
from ..i18n import _
from ..models import User
from pyramid.httpexceptions import HTTPFound
class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Set(),
                                   title=_("User"),
                                   field=User.id)
    user_name = colander.SchemaNode(colander.String(),
                                    title=_("Username"),
                                    field=User.user_name)
    perm_name = colander.SchemaNode(colander.String(),
                                    title=_("Permission"))
    


class CreateSchema(ListSchema):
    pass
class UpdateSchema(ListSchema):
    pass    
  


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = UserPermission
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema  
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = 'user-permission-list'
        self.allow_add = False
        self.allow_view = False
        self.allow_delete = False

    def list_join(self, query):
        return query.join(User, User.id == UserPermission.user_id)
    
    def view_edit(self):
        return HTTPFound(location=self.request.route_url('user-edit', id=self.request.matchdict['id']))
 
        

    
