import colander
from deform import widget, Form
from ..models import Partner, Product, Invoices, InvoiceItems, DBSession
from . import BaseViews
from ..i18n import _

# --- SCHEMAS ---

class InvoiceItemSchema(colander.Schema):
    product_id = colander.SchemaNode(
        colander.Integer(),
        widget=widget.SelectWidget(),
        title=_("Produk")
    )
    qty = colander.SchemaNode(colander.Integer(), title=_("Quantity"), default=1)
    price = colander.SchemaNode(colander.Float(), title=_("Price"))
    amount = colander.SchemaNode(colander.Float(), title=_("Amount"))

    def after_bind(self, schema, appstruct):
        # Mengisi daftar produk ke dropdown
        products = DBSession.query(Product).all()
        schema['product_id'].widget.values = [(p.id, p.name) for p in products]

class InvoiceItemsSequence(colander.SequenceSchema):
    invoice_item = InvoiceItemSchema()

class CreateSchema(colander.Schema):
    code = colander.SchemaNode(colander.String(), title=_("No. Invoice"))
    invoice_date = colander.SchemaNode(colander.Date(), title=_("Tanggal"))
    partner_id = colander.SchemaNode(
        colander.Integer(),
        widget=widget.SelectWidget(),
        title=_("Partner")
    )
    invoice_items = InvoiceItemsSequence(title=_("Daftar Barang"))

    def after_bind(self, schema, appstruct):
        # Mengisi daftar partner ke dropdown
        partners = DBSession.query(Partner).all()
        schema['partner_id'].widget.values = [(p.id, p.name) for p in partners]

class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(), widget=widget.HiddenWidget(), missing=colander.drop)

# --- VIEWS ---

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        # Table utama untuk invoice adalah Invoices, bukan InvoiceItems
        self.table = Invoices 
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.list_route = 'invoice-list'
        self.list_cols = ['id', 'code', 'invoice_date', 'amount', 'partner_id']

    def form_validator(self, form, value):
        id_ = self.request.matchdict.get('id', 0)
        code = value.get('code')
        # Gunakan DBSession untuk query
        row = DBSession.query(self.table).filter(self.table.code == code).first()
        if row and (not id_ or row.id != int(id_)):
            exc = colander.Invalid(form, _('Kesalahan pada pengisian data.'))
            exc["code"] = _('Nomor Invoice {} sudah digunakan.'.format(code))
            raise exc

    def list_join(self, query, **kwargs):
        return query.join(Partner, Partner.id == Invoices.partner_id)

    def save_items(self, invoice, items_data):
        # Hapus items lama sebelum insert yang baru (mencegah duplikat saat update)
        DBSession.query(InvoiceItems).filter(InvoiceItems.invoice_id == invoice.id).delete()
        
        for item in items_data:
            invoice_item = InvoiceItems(
                invoice_id=invoice.id,
                product_id=int(item['product_id']),
                qty=int(item['qty']),
                price=float(item['price']),
                amount=float(item['amount'])
            )
            DBSession.add(invoice_item)
        DBSession.flush()

    def after_create(self, invoice, form_data):
        self.save_items(invoice, form_data.get('invoice_items', []))

    def after_update(self, invoice, form_data):
        self.save_items(invoice, form_data.get('invoice_items', []))