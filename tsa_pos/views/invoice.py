<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
from deform import widget, Form
import colander
from deform.widget import SequenceWidget
from ..models import Partner, Product, Invoices, InvoiceItems
<<<<<<< HEAD
=======
>>>>>>> 3d177a6 (invoice dan form login)
from deform import widget
=======
from deform import widget, Form
>>>>>>> 0010e7b (update invoice)
import colander
from deform.widget import SequenceWidget
from ..models import Partner, Product, Invoices, InvoiceItems
from . import BaseViews
from ..i18n import _

<<<<<<< HEAD
=======
=======
from deform import widget
import colander
from ..models import Invoices, InvoiceItems, Partner, Product
from . import BaseViews
from ..i18n import _

class InvoiceItemSchema(colander.Schema):
    product_id = colander.SchemaNode(
        colander.Integer(),
        widget=widget.SelectWidget(values=[])
    )
    qty = colander.SchemaNode(colander.Integer())
    price = colander.SchemaNode(colander.Float())
    amount = colander.SchemaNode(colander.Float())

    def after_bind(self, schema, appstruct):
        products = Product.query().all()
        schema['product_id'].widget.values = [(str(p.id), p.name) for p in products]

class InvoiceItemsSequence(colander.SequenceSchema):
    invoice_item = InvoiceItemSchema()
>>>>>>> ed1299d (invoice dan form login)

<<<<<<< HEAD
>>>>>>> 3d177a6 (invoice dan form login)
class InvoiceItemSchema(colander.Schema):
    product_id = colander.SchemaNode(
        colander.Integer(),
        widget=widget.SelectWidget(values=[])
    )
    qty = colander.SchemaNode(colander.Integer())
    price = colander.SchemaNode(colander.Float())
    amount = colander.SchemaNode(colander.Float())

    def after_bind(self, schema, appstruct):
        products = Product.query().all()
        schema['product_id'].widget.values = [(str(p.id), p.name) for p in products]

class InvoiceItemsSequence(colander.SequenceSchema):
    invoice_item = InvoiceItemSchema()


class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(), missing=colander.drop, widget=widget.HiddenWidget())
    name = colander.SchemaNode(colander.String())
    code = colander.SchemaNode(colander.String())
    amount = colander.SchemaNode(colander.Float())
    partner_id = colander.SchemaNode(colander.Integer(), title='Partner')
=======
>>>>>>> 0010e7b (update invoice)

class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(), missing=colander.drop, widget=widget.HiddenWidget())
    name = colander.SchemaNode(colander.String())
    code = colander.SchemaNode(colander.String())
    amount = colander.SchemaNode(colander.Float())
    partner_id = colander.SchemaNode(colander.Integer(), title='Partner')

class CreateSchema(colander.Schema):
    name = colander.SchemaNode(colander.String(), validator=colander.Length(min=1, max=128))
    code = colander.SchemaNode(colander.String(), validator=colander.Length(min=1, max=128))
    amount = colander.SchemaNode(colander.Float())
    est_delivery = colander.SchemaNode(colander.DateTime())
    invoice_date = colander.SchemaNode(colander.DateTime())
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 0010e7b (update invoice)
    partner_id = colander.SchemaNode(
        colander.Integer(),
        widget=widget.SelectWidget(values=[]),
        title='Partner'
    )
   
<<<<<<< HEAD
    def after_bind(self, schema, appstruct):
        partners = Partner.query().all()
        schema['partner_id'].widget.values = [(str(p.id), p.name) for p in partners]
class ListSchema (colander.Schema):
    id = colander.SchemaNode(colander.Integer())
    name = colander.SchemaNode(colander.String(), validator=colander.Length(min=1, max=128))
    code = colander.SchemaNode(colander.String(), validator=colander.Length(min=1, max=128))
    amount = colander.SchemaNode(colander.Float())
    est_delivery = colander.SchemaNode(colander.DateTime())
    invoice_date = colander.SchemaNode(colander.DateTime())
    partner_id = colander.SchemaNode(
        colander.Integer(),
        widget=widget.SelectWidget(values=[]),
        title='Partner'
    )
=======
>>>>>>> 3d177a6 (invoice dan form login)
    partner_id = colander.SchemaNode(colander.Integer(), widget=widget.SelectWidget(values=[]))
    invoice_items = InvoiceItemsSequence()

=======
>>>>>>> 0010e7b (update invoice)
    def after_bind(self, schema, appstruct):
        partners = Partner.query().all()
        schema['partner_id'].widget.values = [(str(p.id), p.name) for p in partners]
class ListSchema (colander.Schema):
    id = colander.SchemaNode(colander.Integer())
    name = colander.SchemaNode(colander.String(), validator=colander.Length(min=1, max=128))
    code = colander.SchemaNode(colander.String(), validator=colander.Length(min=1, max=128))
    amount = colander.SchemaNode(colander.Float())
    est_delivery = colander.SchemaNode(colander.DateTime())
    invoice_date = colander.SchemaNode(colander.DateTime())
    partner_id = colander.SchemaNode(
        colander.Integer(),
        widget=widget.SelectWidget(values=[]),
        title='Partner'
    )
    partner_id = colander.SchemaNode(colander.Integer(), widget=widget.SelectWidget(values=[]))
    invoice_items = InvoiceItemsSequence()

    def after_bind(self, schema, appstruct):
        partners = Partner.query().all()
        schema['partner_id'].widget.values = [(str(p.id), p.name) for p in partners]

class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(), missing=colander.drop, widget=widget.HiddenWidget())
<<<<<<< HEAD
<<<<<<< HEAD

<<<<<<< HEAD
=======

>>>>>>> 3d177a6 (invoice dan form login)
=======
    
>>>>>>> 0010e7b (update invoice)
=======

>>>>>>> ed1299d (invoice dan form login)
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
        exc = colander.Invalid(form, 'Kesalahan pada pengisian data.')
        id_ = self.request.matchdict.get('id', 0)
        code = value.get('code')
        row = self.table.query().filter(self.table.code==code).first()
        if row and (not id_ or row.id != int(id_)):
            exc["code"] = _('Code {} sudah ada.'.format(code))
            raise exc

    def list_join(self, query, **kwargs):
        return query.join(Partner, Partner.id==Invoices.partner_id)

    def save_items(self, invoice, items_data):
        InvoiceItems.query().filter(InvoiceItems.invoice_id==invoice.id).delete()
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
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        self.save_items(invoice, form_data.get('invoice_items', []))
=======
        self.save_items(invoice, form_data.get('invoice_items', []))
>>>>>>> 3d177a6 (invoice dan form login)
=======
        self.save_items(invoice, form_data.get('invoice_items', []))
=======
>>>>>>> 84c5a9a (update invoice)
>>>>>>> 0010e7b (update invoice)
=======
        self.save_items(invoice, form_data.get('invoice_items', []))
>>>>>>> f266096 (update invoice)
=======
        self.save_items(invoice, form_data.get('invoice_items', []))
        self.save_items(invoice, form_data.get('invoice_items', []))
>>>>>>> ed1299d (invoice dan form login)
=======
>>>>>>> d670049 (WIP: Perubahan lokal sebelum pull dari main)
=======
        self.save_items(invoice, form_data.get('invoice_items', []))
>>>>>>> 3d177a6 (invoice dan form login)
=======
        self.save_items(invoice, form_data.get('invoice_items', []))
=======
>>>>>>> 84c5a9a (update invoice)
>>>>>>> 0010e7b (update invoice)
=======
        self.save_items(invoice, form_data.get('invoice_items', []))
>>>>>>> f266096 (update invoice)
=======
        self.save_items(invoice, form_data.get('invoice_items', []))
        self.save_items(invoice, form_data.get('invoice_items', []))
>>>>>>> ed1299d (invoice dan form login)
