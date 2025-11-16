from deform import widget
import colander
from ..models import Provinsi
from . import BaseViews
from ..i18n import _


class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             title="Action",
                             widget=widget.HiddenWidget())
    name = colander.SchemaNode(colander.String())


class CreateSchema(colander.Schema):
    # Define your schema fields here
    name = colander.SchemaNode(colander.String(),
                               validator=colander.Length(min=3, max=50))

class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             widget=widget.HiddenWidget())


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Provinsi
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema  
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = 'provinsi-list'

    def form_validator(self, form, value):
        exc = colander.Invalid(
            form,
            'Kesalahan pada pengisian data.'
        )
        id_ = self.request.matchdict.get('id', 0)

        # Validate unique name
        name = value.get('name')
        row = self.table.query().filter(self.table.name == name).first()
        if row and (not id_ or row.id != int(id_)):
            exc["name"] = _(
                'Name {} already exists.'.format(name))
            raise exc
