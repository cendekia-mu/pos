from pyramid.view import view_config
from ..models import Orders, Partner, DBSession
from . import BaseViews
import colander
from deform import widget, Form, ValidationFailure
from ..i18n import _

# DEFINISIKAN DISINI (DI LUAR CLASS)
class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(), title="ID", 
                             missing=colander.drop, 
                             widget=widget.HiddenWidget())
    code = colander.SchemaNode(colander.String(), title=_("Order Code"))
    name = colander.SchemaNode(colander.String(), title=_("Description"))
    partner_id = colander.SchemaNode(colander.Integer(), title=_("Partner"),
                                     widget=widget.SelectWidget(values=[]))
    order_date = colander.SchemaNode(colander.Date(), title=_("Order Date"))
    amount = colander.SchemaNode(colander.Float(), title=_("Total Amount"))
    status = colander.SchemaNode(colander.Integer(), title=_("Status"), default=1)

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Orders 
        self.list_route = 'order-list'
        # SEKARANG ListSchema SUDAH TERDEFINISI DI ATAS
        self.ListSchema = ListSchema 

    def view_list(self):
        return super().view_list()

    def view_add(self):
        # Tambahkan logika form manual jika super().add() tidak ada
        schema = self.ListSchema().bind(request=self.request)
        form = Form(schema, buttons=('save', 'cancel'))
        return {"form": form.render()}

    def view_act(self):
        return super().view_act()