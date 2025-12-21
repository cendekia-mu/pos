import colander
from deform import widget
from ..models import Provinsi
from . import BaseViews
from ..i18n import _

class ListSchema(colander.Schema):
    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        title="Action",
        widget=widget.HiddenWidget()
    )
    name = colander.SchemaNode(colander.String(), title=_("Nama Provinsi"))
    created = colander.SchemaNode(
        colander.DateTime(), 
        title=_("Dibuat"),
        missing=colander.drop
    )

class CreateSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title=_("Nama Provinsi"),
        validator=colander.Length(min=3, max=50)
    )

class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        widget=widget.HiddenWidget()
    )

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
            _('Kesalahan pada pengisian data.')
        )
        id_ = self.request.matchdict.get('id', 0)

        # Validasi nama unik
        name = value.get('name')
        if name:
            row = self.table.query().filter(self.table.name == name).first()
            if row and (not id_ or row.id != int(id_)):
                exc["name"] = _('Name {} already exists.').format(name)
                raise exc