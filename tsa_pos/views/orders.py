from deform import widget
import colander
from tsa_pos.models.partner import Partner
from tsa_pos.widgets import tsa_widget
from ..models import Orders
from . import BaseViews
from ..i18n import _
from datetime import datetime

class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             title="Action",
                             widget=widget.TextInputWidget(readonly=True))
    code = colander.SchemaNode(colander.String(),
                               title="Kode Order")
    name = colander.SchemaNode(colander.String(),
                               title="Keterangan")
    partner_id = colander.SchemaNode(colander.String(),
                                     title="Partner",
                                     field=Partner.name)
    amount = colander.SchemaNode(colander.Decimal(),
                                 title="Total Amount")
    order_date = colander.SchemaNode(colander.DateTime(),
                                     title="Tgl Order")
    status = colander.SchemaNode(colander.Integer(),
                                 title="Status")

class CreateSchema(colander.Schema):
    code = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=1, max=128),
        title="Kode Order")
    
    name = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=1, max=128),
        title="Nama/Keterangan")

    partner_id = colander.SchemaNode(
        colander.Integer(),
        oid="partner_id",
        widget=tsa_widget.Select2Widget(values=[]),
        title="Partner")

    amount = colander.SchemaNode(
        colander.Decimal(),
        default=0,
        title="Total Amount")

    order_date = colander.SchemaNode(
        colander.DateTime(),
        default=datetime.now(),
        title="Tanggal Order",
        widget=widget.DateInputWidget())

    est_delivery = colander.SchemaNode(
        colander.DateTime(),
        missing=colander.drop,
        title="Estimasi Pengiriman",
        widget=widget.DateInputWidget())

    status = colander.SchemaNode(
        colander.Integer(),
        default=0,
        title="Status",
        widget=widget.SelectWidget(values=[
            (0, 'Draft'),
            (1, 'Confirmed'),
            (2, 'Done'),
            (3, 'Cancelled')
        ]))

    def after_bind(self, schema, kw):
        request = kw.get('request')
        partners = Partner.query().order_by(Partner.name).all()
        partner_choices = [(str(p.id), p.name) for p in partners]
        partner_choices.insert(0, ('', 'Pilih Partner...'))
        schema['partner_id'].widget.values = partner_choices

class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             widget=widget.HiddenWidget())

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Orders
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        # Menyesuaikan dengan route: order-list,/order
        self.list_route = 'order-list'

    def form_validator(self, form, value):
        exc = colander.Invalid(form, 'Kesalahan pada pengisian data.')
        id_ = self.request.matchdict.get('id', 0)

        code = value.get('code')
        if code:
            row = self.table.query().filter(self.table.code == code).first()
            if row and (not id_ or row.id != int(id_)):
                exc["code"] = _('Kode Order {} already exists.'.format(code))
                raise exc

    def list_join(self, query):
        return query.outerjoin(Partner, Partner.id == Orders.partner_id)

    # Menangani route: order-act,/order/{act}/act
    def view_act(self):
        act = self.request.matchdict.get('act')
        # Tambahkan logika ajax di sini jika diperlukan
        # Contoh: mengambil harga produk otomatis
        return super().next_act()

    # Menangani route: order-checkout,/order/{id}/checkout
    def view_checkout(self):
        id_ = self.request.matchdict.get('id')
        row = self.table.query().filter(self.table.id == id_).first()
        if not row:
            return {"error": "Data tidak ditemukan"}
        
        # Logika checkout Anda di sini (misal: merubah status menjadi 'Done')
        # row.status = 2 
        return {"id": id_, "status": "processed"}