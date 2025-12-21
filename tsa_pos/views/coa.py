from deform import widget
import colander
from ..models import Coa  # Pastikan model Coa diimpor dengan benar
from . import BaseViews
from ..i18n import _

class ListSchema(colander.Schema):
    # Skema untuk list view (menampilkan data Coa dalam tabel)
    # Hanya definisikan field yang akan ditampilkan/di-edit di list
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             title="ID",
                             widget=widget.HiddenWidget())
    name = colander.SchemaNode(colander.String(),
                               title="Name")
    code = colander.SchemaNode(colander.String(),
                               title="Code")
    parent_id = colander.SchemaNode(colander.Integer(),
                                    missing=colander.drop,
                                    title="Parent ID",
                                    widget=widget.HiddenWidget())  # Atau gunakan SelectWidget jika perlu dropdown
    status = colander.SchemaNode(colander.Integer(),
                                 title="Status",
                                 validator=colander.OneOf([0, 1]),  # Misal 0=inactive, 1=active
                                 widget=widget.SelectWidget(values=[(0, 'Inactive'), (1, 'Active')]))

class CreateSchema(colander.Schema):
    # Skema untuk create form
    name = colander.SchemaNode(colander.String(),
                               validator=colander.Length(min=3, max=128),  # Sesuaikan panjang berdasarkan model
                               title="Name")
    code = colander.SchemaNode(colander.String(),
                               validator=colander.Length(min=1, max=128),
                               title="Code")
    parent_id = colander.SchemaNode(colander.Integer(),
                                    missing=colander.drop,  # Opsional untuk root Coa
                                    title="Parent Coa",
                                    widget=widget.SelectWidget(values=[]))  # Isi values dengan query Coa aktif
    status = colander.SchemaNode(colander.Integer(),
                                 missing=1,  # Default active
                                 title="Status",
                                 validator=colander.OneOf([0, 1]),
                                 widget=widget.SelectWidget(values=[(0, 'Inactive'), (1, 'Active')]))

class UpdateSchema(CreateSchema):
    # Update schema mirip Create, tapi tambah id (hidden)
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             widget=widget.HiddenWidget())

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Coa  # Ubah dari ProductCategory ke Coa
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema  
        self.ReadSchema = UpdateSchema  # Read bisa sama dengan Update
        self.ListSchema = ListSchema
        self.list_route = 'coa-list'  # Sesuaikan dengan route name di aplikasi Anda

    def form_validator(self, form, value):
        exc = colander.Invalid(
            form,
            'Kesalahan pada pengisian data.'
        )
        id_ = self.request.matchdict.get('id', 0)

        # Validate unique name
        name = value.get('name')
        if name:
            row = self.table.query().filter(self.table.name == name).first()
            if row and (not id_ or row.id != int(id_)):
                exc["name"] = _(
                    'Name {} already exists.'.format(name))
                raise exc

        # Tambahan: Validate unique code (karena code unik di model)
        code = value.get('code')
        if code:
            row = self.table.query().filter(self.table.code == code).first()
            if row and (not id_ or row.id != int(id_)):
                exc["code"] = _(
                    'Code {} already exists.'.format(code))
                raise exc

        # Tambahan: Validate parent_id (pastikan parent ada dan tidak self-referential)
        parent_id = value.get('parent_id')
        if parent_id:
            parent = self.table.query().filter(self.table.id == parent_id).first()
            if not parent:
                exc["parent_id"] = _('Parent Coa does not exist.')
                raise exc
            if id_ and int(id_) == parent_id:
                exc["parent_id"] = _('Cannot set self as parent.')
                raise exc