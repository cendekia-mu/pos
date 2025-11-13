import email
from deform import widget
from marshmallow import missing
import colander
import deform
import re
from ..models import User
from . import BaseViews
from ..i18n import _
class ListSchema(colander.Schema):    
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             title="Action",
                             widget = widget.HiddenWidget())
    user_name = colander.SchemaNode(colander.String())
    email = colander.SchemaNode(colander.String(), validator=colander.Email())
    last_login_date = colander.SchemaNode(colander.DateTime(),
                                            missing=colander.drop)

class CreateSchema(colander.Schema):    
    # Define your schema fields here
    user_name = colander.SchemaNode(colander.String())
    email = colander.SchemaNode(colander.String(), validator=colander.Email())
    password = colander.SchemaNode(colander.String(), widget=deform.widget.PasswordWidget(),
                                   missing=colander.drop,)

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
        self.ListSchema = ListSchema
        self.list_route = 'user-list'

    def form_validator(self, form, value):
        id_ = self.request.matchdict.get('id', 0)
        user_name = value.get('username')
        email = value.get('email')
        exc = colander.Invalid(
            form,
            'Kesalahan pada pengisian data.'
        )
        row = User.query().filter(
            (User.user_name == user_name)
        ).first()
        if row and (not id_ or row.id != int(id_)):
            exc["username"] = _('User Name {} already exists.'.format(user_name))
            raise exc
        row = User.query().filter(User.email == email).first()
        if row and (not id_ or row.id != int(id_)):
            exc["email"] = _('Email {} already exists.'.format(email))
            raise exc
        password = value.get('password')
        if password:
            pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%#*?&])[A-Za-z\d@$!#%*?&]{8,}$')
    
            if not bool(pattern.fullmatch(password)):
                exc["password"] = _('Password must be at least 8 characters long. It must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.')
                raise exc
            


