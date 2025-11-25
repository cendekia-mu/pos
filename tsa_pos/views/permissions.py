from deform import widget
import colander
import deform
import re
from ..models import Permissions
from . import BaseViews
from ..i18n import _


class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             title="Action",
                             widget=widget.HiddenWidget())
    name = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String())


class CreateSchema(colander.Schema):
    # Define your schema fields here
    name = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(
        colander.String())



class UpdateSchema(ListSchema):
    pass

class ReadSchema(ListSchema):
    pass


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Permissions  # Assuming User is your SQLAlchemy model
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema  # For simplicity, using the same schema
        self.ReadSchema = ReadSchema  # For simplicity, using the same schema
        self.ListSchema = ListSchema
        self.list_route = 'permissions-list'

    def validator(self, id_, value, form):
        name = value.get('name')
        exc = colander.Invalid(
            form,
            'Kesalahan pada pengisian data.'
        )
        row = self.table.query().filter(
            self.table.name == name
        ).first()
        if row and (not id_ or row.id != int(id_)):
            exc["name"] = _(
                'Name {} already exists.'.format(name))
            raise exc