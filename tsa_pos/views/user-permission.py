from deform import widget
import colander
from ..models import UserPermission
from . import BaseViews
from ..i18n import _
from ..models import User
class ListSchema(colander.Schema):
    user_id = colander.SchemaNode(colander.Set(),
                                   title=_("User"),
                                   widget=widget.CheckboxChoiceWidget(values=[]),)
    perm_name = colander.SchemaNode(colander.String(),
                                    title=_("Permission"))

    def after_bind(self, schema, appstruct):

        users = User.query().all()
        schema['user_id'].widget.values = [
            (str(g.id), g.user_name) for g in users
        ]
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

 
        

    
