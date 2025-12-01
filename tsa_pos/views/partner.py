from deform import widget
import colander
from ..models import Partner
from . import BaseViews
from ..i18n import _


class ListSchema(colander.Schema):
    action = colander.SchemaNode(colander.String(),
                                 missing=colander.drop,
                                 title="Action",
                                 widget=widget.TextInputWidget(readonly=True))  # Untuk tombol/link aksi
    kode = colander.SchemaNode(colander.String(),
                               title="Kode")
    name = colander.SchemaNode(colander.String(),
                               title="Nama")
    type = colander.SchemaNode(colander.String(),
                               title="Tipe")  # Gabungan dari is_vendor dan is_customer, e.g., "Vendor", "Customer", atau "Vendor & Customer"
    location = colander.SchemaNode(colander.String(),
                                   title="Lokasi")  # Gabungan alamat lengkap
    balance = colander.SchemaNode(colander.Decimal(),
                                  title="Balance")

class CreateSchema(colander.Schema):
    kode = colander.SchemaNode(colander.String(),
                               validator=colander.Length(min=1, max=20))
    name = colander.SchemaNode(colander.String(),
                               validator=colander.Length(min=3, max=50))
    is_vendor = colander.SchemaNode(colander.Integer(),
                                    title="Is Vendor",
                                    widget=widget.CheckboxWidget(true_val='1', false_val='0'), 
                                    default=0)
    is_customer = colander.SchemaNode(colander.Integer(),
                                      title="Is Customer",
                                      widget= widget.CheckboxWidget(true_val='1', false_val='0'),
                                      default=1)
    address_1 = colander.SchemaNode(colander.String(),
                                    validator=colander.Length(min=1, max=100),
                                    title="Alamat 1",
                                    widget=widget.TextAreaWidget())  # Menggunakan TextAreaWidget berdasarkan spesifikasi "Alamat" sebagai Textarea
    address_2 = colander.SchemaNode(colander.String(),
                                    missing=colander.drop,
                                    title="Alamat 2",
                                    widget=widget.TextAreaWidget())  # Menggunakan TextAreaWidget untuk konsistensi
    kelurahan = colander.SchemaNode(colander.String(),
                                     validator=colander.Length(min=1, max=50),
                                     title="Kelurahan")
    # kota = colander.SchemaNode(colander.String(),
    #                            title="Kota")  # Diubah menjadi String untuk input huruf
    # provinsi = colander.SchemaNode(colander.String(),
    #                                title="Provinsi")  # Diubah menjadi String untuk input huruf
    # balance = colander.SchemaNode(colander.Decimal(),
    #                               default=0.0,
    #                               title="Balance (Rupiah)")  # Ditambahkan "(Rupiah)" untuk menunjukkan ini untuk pembayaran dalam rupiah

class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             widget=widget.HiddenWidget())

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Partner
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema  
        self.ReadSchema = UpdateSchema  # Asumsi ReadSchema sama dengan UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = 'partner-list'

    def form_validator(self, form, value):
        exc = colander.Invalid(
            form,
            'Kesalahan pada pengisian data.'
        )
        id_ = self.request.matchdict.get('id', 0)

        # Validate unique kode
        kode = value.get('kode')
        if kode:
            row = self.table.query().filter(self.table.kode == kode).first()
            if row and (not id_ or row.id != int(id_)):
                exc["kode"] = _(
                    'Kode {} already exists.'.format(kode))
                raise exc

        # Validate unique name
        name = value.get('name')
        if name:
            row = self.table.query().filter(self.table.name == name).first()
            if row and (not id_ or row.id != int(id_)):
                exc["name"] = _(
                    'Name {} already exists.'.format(name))
                raise exc

    # Metode tambahan untuk list view, jika diperlukan (misalnya untuk menggabungkan data lokasi dan tipe)
    def list_view(self):
        # Logika untuk mengambil data dan menggabungkan field seperti location dan type
        # Contoh: Gabungkan alamat menjadi satu string untuk location
        # Gabungkan is_vendor dan is_customer menjadi string tipe
        # Ini bisa dilakukan di query atau di template
        pass
