from deform import widget
from marshmallow import missing
import colander
import deform
from ..models import User
from . import BaseViews

class CreateSchema(colander.Schema):    
    # Define your schema fields here
    user_name = colander.SchemaNode(colander.String())
    email = colander.SchemaNode(colander.String(), validator=colander.Email())
    password = colander.SchemaNode(colander.String(), widget=deform.widget.PasswordWidget())

class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             widget = widget.HiddenWidget())

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = User  # Assuming User is your SQLAlchemy model
        self.CreateSchema = CreateSchema
        self.UpdateSchema = CreateSchema  # For simplicity, using the same schema
        self.ReadSchema = CreateSchema  # For simplicity, using the same schema
        self.list_route_name = 'user-list'

