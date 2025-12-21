from pyramid.view import view_config
from ..models import Orders, Partner, DBSession
from . import BaseViews
import colander
from deform import widget
from ..i18n import _

class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(), title="ID")
    code = colander.SchemaNode(colander.String(), title=_("Order Code"))
    name = colander.SchemaNode(colander.String(), title=_("Description"))
    partner_id = colander.SchemaNode(colander.Integer(), title=_("Partner"),
                                     widget=widget.SelectWidget(values=[]))
    order_date = colander.SchemaNode(colander.DateTime(), title=_("Order Date"))
    amount = colander.SchemaNode(colander.Float(), title=_("Total Amount"))
    status = colander.SchemaNode(colander.Integer(), title=_("Status"))

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Orders 
        self.list_route = 'order-list'
        self.ListSchema = ListSchema

    # Handler AJAX untuk /order/grid/act (Mencegah Ajax Error 404)
    def view_act(self):
        return super().view_act()

    # Handler Tampilan List
    def view_list(self):
        return super().view_list()

    # Placeholders untuk route lain agar tidak 404
    def view_create(self):
        return super().add()

    def view_read(self):
        return super().view_read()

    def view_checkout(self):
        return {"title": "Checkout Order"}