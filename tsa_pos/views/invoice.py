from deform import widget, Form
import colander
from tsa_pos.widgets import tsa_widget

from ..models import Partner, Product, Invoices, InvoiceItems
from . import BaseViews
from ..i18n import _


class ListSchema(colander.Schema):
    id = colander.SchemaNode(
        colander.Integer(), missing=colander.drop, widget=widget.HiddenWidget()
    )
    name = colander.SchemaNode(colander.String())
    code = colander.SchemaNode(colander.String())
    amount = colander.SchemaNode(colander.Float())
    partner_id = colander.SchemaNode(colander.Integer(), title="Partner")


class CreateSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(), validator=colander.Length(min=1, max=128)
    )
    code = colander.SchemaNode(
        colander.String(), validator=colander.Length(min=1, max=128)
    )
    amount = colander.SchemaNode(colander.Float())
    est_delivery = colander.SchemaNode(
        colander.String(), widget=tsa_widget.BootStrapDateInputWidget()
    )
    invoice_date = colander.SchemaNode(
        colander.String(), widget=tsa_widget.BootStrapDateInputWidget()
    )
    partner_id = colander.SchemaNode(
        colander.Integer(), widget=widget.SelectWidget(values=[]), title="Partner"
    )

    def after_bind(self, schema, appstruct):
        partners = Partner.query().all()
        schema["partner_id"].widget.values = [(str(p.id), p.name) for p in partners]


class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer())
    name = colander.SchemaNode(
        colander.String(), validator=colander.Length(min=1, max=128)
    )
    code = colander.SchemaNode(
        colander.String(), validator=colander.Length(min=1, max=128)
    )
    amount = colander.SchemaNode(colander.Float())
    est_delivery = colander.SchemaNode(
        colander.String(), widget=tsa_widget.BootStrapDateInputWidget()
    )
    invoice_date = colander.SchemaNode(
        colander.String(), widget=tsa_widget.BootStrapDateInputWidget()
    )
    partner_id = colander.SchemaNode(
        colander.Integer(), widget=widget.SelectWidget(values=[]), title="Partner"
    )
    partner_id = colander.SchemaNode(
        colander.Integer(), widget=widget.SelectWidget(values=[])
    )

    def after_bind(self, schema, appstruct):
        partners = Partner.query().all()
        schema["partner_id"].widget.values = [(str(p.id), p.name) for p in partners]


class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(
        colander.Integer(), missing=colander.drop, widget=widget.HiddenWidget()
    )


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Invoices
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = "invoice-list"

    def form_validator(self, form, value):
        exc = colander.Invalid(form, "Kesalahan pada pengisian data.")
        id_ = self.request.matchdict.get("id", 0)
        code = value.get("code")
        row = self.table.query().filter(self.table.code == code).first()
        if row and (not id_ or row.id != int(id_)):
            exc["code"] = _("Code {} sudah ada.".format(code))
            raise exc