import colander
from deform import widget, Form
from deform.widget import SequenceWidget
from ..models import Partner, Product, Invoices, InvoiceItems, DBSession
from . import BaseViews
from ..i18n import _

# --- SCHEMAS ---

class InvoiceItemSchema(colander.Schema):
    product_id = colander.SchemaNode(
        colander.Integer(),
        widget=widget.SelectWidget(values=[]),
        title=_('Produk')
    )
    qty = colander.SchemaNode(colander.Integer(), title=_('Qty'), default=1)
    price = colander.SchemaNode(colander.Float(), title=_('Harga'))
    amount = colander.SchemaNode(colander.Float(), title=_('Total'))

    def after_bind(self, schema, appstruct):
        # Mengisi dropdown produk secara dinamis
        products = Product.query().all()
        schema['product_id'].widget.values = [(str(p.id), p.name) for p in products]

class InvoiceItemsSequence(colander.SequenceSchema):
    invoice_item = InvoiceItemSchema()

class CreateSchema(colander.Schema):
    code = colander.SchemaNode(
        colander.String(), 
        validator=colander.Length(min=1, max=128),
        title=_('No. Invoice')
    )
    name = colander.SchemaNode(
        colander.String(), 
        validator=colander.Length(min=1, max=128),
        title=_('Nama Transaksi')
    )
    invoice_date = colander.SchemaNode(colander.DateTime(), title=_('Tgl Invoice'))
    est_delivery = colander.SchemaNode(colander.DateTime(), title=_('Est. Pengiriman'))
    partner_id = colander.SchemaNode(
        colander.Integer(),
        widget=widget.SelectWidget(values=[]),
        title=_('Partner')
    )
    amount = colander.SchemaNode(colander.Float(), title=_('Total Keseluruhan'))
    invoice_items = InvoiceItemsSequence(title=_('Daftar Barang'))

    def after_bind(self, schema, appstruct):
        # Mengisi dropdown partner secara dinamis
        partners = Partner.query().all()
        schema['partner_id'].widget.values = [(str(p.id), p.name) for p in partners]

class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(), missing=colander.drop, widget=widget.HiddenWidget())

class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer())
    code = colander.SchemaNode(colander.String())
    name = colander.SchemaNode(colander.String())
    amount = colander.SchemaNode(colander.Float())
    invoice_date = colander.SchemaNode(colander.DateTime())
    partner_id = colander.SchemaNode(colander.Integer(), title=_('Partner'))

# --- VIEWS ---

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Invoices
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = 'invoice-list'

    def form_validator(self, form, value):
        id_ = self.request.matchdict.get('id', 0)
        code = value.get('code')
        row = self.table.query().filter(self.table.code == code).first()
        if row and (not id_ or row.id != int(id_)):
            exc = colander.Invalid(form, _('Kesalahan pada pengisian data.'))
            exc["code"] = _('Code {} sudah ada.'.format(code))
            raise exc

    def list_join(self, query, **kwargs):
        return query.join(Partner, Partner.id == Invoices.partner_id)

    def save_items(self, invoice, items_data):
        # Hapus item lama (delete-orphan style)
        InvoiceItems.query().filter(InvoiceItems.invoice_id == invoice.id).delete()
        
        for item in items_data:
            invoice_item = InvoiceItems(
                invoice_id=invoice.id,
                product_id=int(item['product_id']),
                qty=int(item['qty']),
                price=float(item['price']),
                amount=float(item['amount'])
            )
            self.db_session.add(invoice_item)
        self.db_session.flush()

    def after_create(self, invoice, form_data):
        self.save_items(invoice, form_data.get('invoice_items', []))

    def after_update(self, invoice, form_data):
        self.save_items(invoice, form_data.get('invoice_items', []))