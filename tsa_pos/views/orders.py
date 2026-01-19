from deform import widget, Form
import colander
from tsa_pos.widgets import tsa_widget
from ..models import Partner, Product, Orders 
from . import BaseViews
from ..i18n import _

class CreateSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(), missing=colander.drop, widget=widget.HiddenWidget())
    name = colander.SchemaNode(colander.String(), validator=colander.Length(min=1, max=128))
    code = colander.SchemaNode(colander.String(), validator=colander.Length(min=1, max=128))
    amount = colander.SchemaNode(colander.Float(), missing=0)
    order_date = colander.SchemaNode(colander.String(), widget=tsa_widget.BootStrapDateInputWidget())
    est_delivery = colander.SchemaNode(colander.String(), widget=tsa_widget.BootStrapDateInputWidget())
    status = colander.SchemaNode(colander.Integer(), widget=widget.SelectWidget(values=[(0, 'Draft'), (1, 'Confirmed')]))
    partner_id = colander.SchemaNode(colander.Integer(), widget=widget.SelectWidget(values=[]), title="Partner")

class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer())
    name = colander.SchemaNode(colander.String())
    code = colander.SchemaNode(colander.String())
    amount = colander.SchemaNode(colander.Float())
    order_date = colander.SchemaNode(colander.String())
    est_delivery = colander.SchemaNode(colander.String())
    status = colander.SchemaNode(colander.Integer())
    partner_id = colander.SchemaNode(colander.Integer())

class UpdateSchema(CreateSchema):
    pass

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Orders
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = "order-list"

    def after_bind(self, schema, kw):
        # Mengisi dropdown partner
        partners = Partner.query().all()
        if 'partner_id' in schema:
            schema['partner_id'].widget.values = [(str(p.id), p.name) for p in partners]

    def list_join(self, query):
        # Sangat penting: Join ke partner agar grid bisa render partner_id
        return query.outerjoin(Partner, Partner.id == Orders.partner_id)

    def view_act(self):
        # Endpoint untuk Ajax DataTables
        return self.grid_data()