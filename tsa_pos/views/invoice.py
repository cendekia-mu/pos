from deform import widget, Form
import colander
from deform.widget import SequenceWidget

from tsa_pos.views import invoice_items
from tsa_pos.widgets import tsa_widget
from ..models import Partner, Product, Invoices, InvoiceItems
from . import BaseViews
from ..i18n import _


class CreateSchema(colander.Schema):
    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        title="ID",
        widget=widget.HiddenWidget(),
    )

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
    invoice_items = colander.SchemaNode(
        colander.String(), widget=tsa_widget.BootStrapDateInputWidget()
    )
    partner_id = colander.SchemaNode(
        colander.Integer(), widget=widget.SelectWidget(values=[]), title="Partner"
    )

    def after_bind(self, schema, appstruct):
        partners = Partner.query().all()
        schema["partner_id"].widget.values = [(str(p.id), p.name) for p in partners]


class ListSchema(colander.Schema):
    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        title="ID",
        widget=widget.HiddenWidget(),
    )

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

    invoice_items = colander.SchemaNode(
        colander.String(), widget=tsa_widget.BootStrapDateInputWidget()
    )

    partner_id = colander.SchemaNode(
        colander.Integer(), widget=widget.SelectWidget(values=[]), title="Partner"
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