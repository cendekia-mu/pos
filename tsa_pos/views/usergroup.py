from deform import widget
import colander
from ..models import  UserGroup,User,Group
from . import BaseViews
from ..i18n import _



class ListSchema(colander.Schema):
    user_name = colander.SchemaNode(colander.String(),
                                  title="Username",
                                  field=User.user_name)
                                #  )

    group_name = colander.SchemaNode(colander.String(),
                                   title="Group ID",
                                   field=Group.group_name)
                                   

    # user_name = colander.SchemaNode(colander.String(),
    #                                 title="Username",
    #                                 field=User.user_name)

    # group_name = colander.SchemaNode(colander.String(),
    #                                  title="Group Name",
    #                                  field=Group.group_name)



class CreateSchema(ListSchema):
    pass
class UpdateSchema(ListSchema):
    pass    
  


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = UserGroup
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema  
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = 'user-group-list'
        self.list_buttons = ''

    def list_join(self, query):
        return (query.join(User, User.id == UserGroup.user_id)
                .join(Group, Group.id == UserGroup.group_id))

    
