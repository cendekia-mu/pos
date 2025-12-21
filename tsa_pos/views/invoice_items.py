from tkinter.tix import Form
import colander
from deform import widget, Form
from ..models import Product
from ..views import BaseViews
from ..models import Partner, Product, Invoices, InvoiceItems
from . import BaseViews
from ..i18n import _


# Invoice Item Schema
class InvoiceItemSchema(colander.Schema):
    product_id = colander.SchemaNode(
        colander.Integer(), widget=widget.SelectWidget(values=[]), title="Product"
    )
    qty = colander.SchemaNode(colander.Integer(), title="Quantity")
    price = colander.SchemaNode(colander.Float(), title="Price")
    amount = colander.SchemaNode(colander.Float(), title="Amount")

    def after_bind(self, schema, appstruct):
        products = Product.query().all()
        schema["product_id"].widget.values = [(str(p.id), p.name) for p in products]


# Sequence Schema
class InvoiceItemsSequence(colander.SequenceSchema):
    invoice_item = InvoiceItemSchema()


class CreateSchema(colander.Schema):
    pass


class UpdateSchema(CreateSchema):
    pass


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = InvoiceItems
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.ListSchema = None
        self.list_route = "invoice-items-list"
        self.list_cols = [
            "id",
            "name",
            "code",
            "amount",
            "partner_id",
        ]  # list view columns

    # Validator unik code
    def form_validator(self, form, value):
        exc = colander.Invalid(form, "Kesalahan pada pengisian data.")
        id_ = self.request.matchdict.get("id", 0)
        code = value.get("code")
        row = self.table.query().filter(self.table.code == code).first()
        if row and (not id_ or row.id != int(id_)):
            exc["code"] = _("Code {} sudah ada.".format(code))
            raise exc

    # Join partner untuk list view
    def list_join(self, query, **kwargs):
        return query.join(Partner, Partner.id == Invoices.partner_id)

    # Simpan invoice items
    def save_items(self, invoice, items_data):
        InvoiceItems.query().filter(InvoiceItems.invoice_id == invoice.id).delete()
        for item in items_data:
            invoice_item = InvoiceItems(
                invoice_id=invoice.id,
                product_id=int(item["product_id"]),
                qty=int(item["qty"]),
                price=float(item["price"]),
                amount=float(item["amount"]),
            )
            self.db_session.add(invoice_item)
        self.db_session.flush()

    # Hook setelah create/update
    def after_create(self, invoice, form_data):
        self.save_items(invoice, form_data.get("invoice_items", []))

    def after_update(self, invoice, form_data):
        self.save_items(invoice, form_data.get("invoice_items", []))

    # Render form deform
    def create_view(self):
        schema = self.CreateSchema()
        form = Form(schema, buttons=("submit",))
        return {"form": form.render(), "scripts": []}  # scripts penting untuk template

    def update_view(self, id_):
        schema = self.UpdateSchema()
        form = Form(schema, buttons=("submit",))
        return {"form": form.render(), "scripts": []}

    def list_view(self):
        query = self.table.query()
        query = self.list_join(query)
        items = query.all()
        return {
            "items": items,
            "list_cols": self.list_cols,
            "list_route": self.list_route,
            "scripts": [],  # untuk template list.pt
        }
