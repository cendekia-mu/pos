import colander
from deform import widget

from ..models import PaymentItems, Payment, Invoices, Partner
from . import BaseViews
from ..i18n import _


    # =========================
    # LIST (Tampilan Tabel)
    # =========================
class ListSchema(colander.Schema):
        id = colander.SchemaNode(colander.Integer(),
                                missing=colander.drop,
                                title="Action",
                                widget=widget.HiddenWidget())
        payment_id = colander.SchemaNode(
            colander.Integer(),
            title=_("Payment ID"),
        )

        partner_nama = colander.SchemaNode(
            colander.String(),
            title=_("Nama Partner"),
        )

        invoice_code = colander.SchemaNode(
            colander.String(),
            title=_("Invoice"),
        )

        amount = colander.SchemaNode(
            colander.Float(),
            title=_("Amount"),
        )


    # =========================
    # CREATE / UPDATE (Form)
    # =========================
class CreateSchema(colander.Schema):

        payment_id = colander.SchemaNode(
            colander.Integer(),
            title=_("Payment"),
            widget=widget.SelectWidget(values=[]),
        )

        invoice_id = colander.SchemaNode(
            colander.Integer(),
            title=_("Invoice"),
            widget=widget.SelectWidget(values=[]),
        )

        amount = colander.SchemaNode(
            colander.Float(),
            title=_("Amount"),
        )

        def after_bind(self, schema, appstruct):
            payments = (
                Payment.query()
                .join(Partner, Payment.partner_id == Partner.id)
                .with_entities(
                    Payment.id,
                    Partner.name.label("partner_name"),
                )
                .all()
            )

            schema["payment_id"].widget.values = [
                (p.id, p.partner_name) for p in payments
            ]

            invoices = Invoices.query().all()
            schema["invoice_id"].widget.values = [
                (i.id, i.code) for i in invoices
            ]



class UpdateSchema(CreateSchema):
        payment_id = colander.SchemaNode(
            colander.Integer(),
            widget=widget.HiddenWidget(),
            missing=colander.drop,
        )

        invoice_id = colander.SchemaNode(
            colander.Integer(),
            widget=widget.HiddenWidget(),
            missing=colander.drop,
        )


    # =========================
    # VIEWS
    # =========================
class Views(BaseViews):
    def __init__(self, request):
                super().__init__(request)
                self.table = PaymentItems
                self.ListSchema = ListSchema
                self.CreateSchema = CreateSchema
                self.UpdateSchema = UpdateSchema
                self.ReadSchema = UpdateSchema
                self.list_route = "payment-items-list"
                self.column_filter = True

    def list_join(self, query):
                return (
                    query
                    .join(Payment, Payment.id == PaymentItems.payment_id)
                    .join(Partner, Partner.id == Payment.partner_id)
                    .join(Invoices, Invoices.id == PaymentItems.invoice_id)
                )

    def list_columns(self):
                return [
                    PaymentItems.id.label("id"),
                    PaymentItems.payment_id.label("payment_id"),
                    Partner.name.label("partner_nama"),
                    Invoices.code.label("invoice_code"),
                    PaymentItems.amount.label("amount"),
                ]

    def form_validator(self, form, value):
                exc = colander.Invalid(form, _("Kesalahan pada pengisian data"))

                payment_id = value.get("payment_id")
                invoice_id = value.get("invoice_id")

                exists = (
                    PaymentItems.query()
                    .filter(
                        PaymentItems.payment_id == payment_id,
                        PaymentItems.invoice_id == invoice_id,
                    )
                    .first()
                )

                if exists:
                    exc["payment_id"] = _("Item payment ini sudah ada di invoice terpilih")
                    raise exc
