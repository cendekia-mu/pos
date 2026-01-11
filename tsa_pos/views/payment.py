import colander
from deform import widget

from ..models import Payment, Partner
from . import BaseViews
from ..i18n import _


# =========================
# LIST
# =========================
class ListSchema(colander.Schema):
    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        widget=widget.HiddenWidget(),
    )

    partner = colander.SchemaNode(
        colander.String(),
        title="Partner",
        field=Partner.kode,
    )

    amount = colander.SchemaNode(
        colander.Float(),
        title="Amount",
    )

    description = colander.SchemaNode(
        colander.String(),
        missing="",
        title="Description",
    )


# =========================
# CREATE / UPDATE
# =========================
class CreateSchema(colander.Schema):
    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        widget=widget.HiddenWidget(),
    )

    partner_id = colander.SchemaNode(
        colander.Integer(),
        title="Partner",
        widget=widget.SelectWidget(values=[]),
    )

    amount = colander.SchemaNode(
        colander.Float(),
        title="Amount",
        widget=widget.TextInputWidget(css_class="form-control"),
    )

    description = colander.SchemaNode(
        colander.String(),
        missing="",
        title="Description",
        widget=widget.TextAreaWidget(rows=3, css_class="form-control"),
    )

    def after_bind(self, schema, appstruct):
        partners = Partner.query().all()
        choices = [(str(p.id), p.kode) for p in partners]
        choices.insert(0, ("", "Pilih Partner"))

        schema["partner_id"].widget.values = choices

        if appstruct is None:
            schema["amount"].default = 0


class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        widget=widget.HiddenWidget(),
    )


# =========================
# VIEWS
# =========================
class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Payment
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = "payment-list"

    def list_join(self, query):
        return query.outerjoin(
            Partner, Partner.id == Payment.partner_id
        )

    def form_validator(self, form, value):
        exc = colander.Invalid(form, "Kesalahan pada pengisian data.")

        partner_id = value.get("partner_id")
        id_ = self.request.matchdict.get("id")

        # CEK PARTNER SUDAH ADA ATAU BELUM
        q = Payment.query().filter(
            Payment.partner_id == partner_id
        )

        # kalau update, abaikan record sendiri
        if id_:
            q = q.filter(Payment.id != int(id_))

        if q.first():
            exc["partner_id"] = _(
                "Partner ini sudah memiliki payment, tidak boleh dobel."
            )
            raise exc

        # VALIDASI AMOUNT
        amount = value.get("amount")
        if amount is not None and amount <= 0:
            exc["amount"] = _("Amount must be greater than 0")
            raise exc
