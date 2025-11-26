from deform import widget
import colander
from ..models import GroupPermission, UserGroup
from . import BaseViews
from ..i18n import _


class ListSchema(colander.Schema):
    user_id = colander.SchemaNode(colander.String(),
                                  title=_("User"))
    group_id = colander.SchemaNode(colander.String(),
                                   title=_("Group"))


  


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = UserGroup
        self.ListSchema = ListSchema
        self.list_route = 'user-group-list'

    
