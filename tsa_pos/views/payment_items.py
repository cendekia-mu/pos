import colander
from deform import widget

from ..models import Payment, PaymentItems, Invoices
from . import BaseViews
from ..i18n import _
class CreateSchema(colander.Schema):
    payment_id = colander.SchemaNode(
        colander.Integer(),
        widget=widget.HiddenWidget(),
    )

    invoice_id = colander.SchemaNode(
        colander.Integer(),
        title="Invoice",
        widget=widget.SelectWidget(values=[]),
    )

    amount = colander.SchemaNode(
        colander.Float(),
        title="Amount",
        widget=widget.TextInputWidget(css_class="form-control"),
    )

    def after_bind(self, schema, appstruct):
        invoices = Invoices.query().all()
        choices = [(str(i.id), i.number) for i in invoices]
        choices.insert(0, ("", "Pilih Invoice"))

        schema["invoice_id"].widget.values = choices

        if appstruct is None:
            schema["amount"].default = 0
class UpdateSchema(CreateSchema):
    pass
class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = PaymentItems
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.list_route = "payment_items"
    def form_validator(self, form, value):
        exc = colander.Invalid(form, "Kesalahan pada pengisian data.")

        payment_id = value.get("payment_id")
        invoice_id = value.get("invoice_id")
        amount = value.get("amount")

        # AMOUNT HARUS > 0
        if amount is not None and amount <= 0:
            exc["amount"] = _("Amount must be greater than 0")
            raise exc

        # CEK PAYMENT ADA
        payment = Payment.query().get(payment_id)
        if not payment:
            raise exc

        # CEK INVOICE TIDAK BOLEH DOBEL
        q = PaymentItems.query().filter(
            PaymentItems.payment_id == payment_id,
            PaymentItems.invoice_id == invoice_id
        )

        if q.first():
            exc["invoice_id"] = _("Invoice ini sudah ada di payment.")
            raise exc
    def after_save(self, obj, form):
        payment = Payment.query().get(obj.payment_id)

        payment.amount = sum(
            item.amount for item in payment.payment_items
        )
    def after_delete(self, obj):
        payment = Payment.query().get(obj.payment_id)
        if payment:
            payment.amount = sum(
                item.amount for item in payment.payment_items
            )
