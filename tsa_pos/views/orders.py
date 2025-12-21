from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from ..models import Orders, Partner, DBSession
from . import BaseViews
import colander
from deform import widget, Form, ValidationFailure
from ..i18n import _
import datetime

class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(), title="ID", 
                             missing=colander.drop, 
                             widget=widget.HiddenWidget())
    code = colander.SchemaNode(colander.String(), title=_("Order Code"))
    name = colander.SchemaNode(colander.String(), title=_("Description"))
    partner_id = colander.SchemaNode(colander.Integer(), title=_("Partner"),
                                     widget=widget.SelectWidget(values=[]))
    order_date = colander.SchemaNode(colander.Date(), title=_("Order Date"),
                                     default=datetime.date.today())
    amount = colander.SchemaNode(colander.Float(), title=_("Total Amount"), default=0)
    status = colander.SchemaNode(colander.Integer(), title=_("Status"), default=1)

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Orders 
        self.list_route = 'order-list'
        self.ListSchema = ListSchema

    # Fungsi pembantu untuk redirect ke halaman list
    def redirect_list(self):
        return HTTPFound(location=self.request.route_url(self.list_route))

    def view_list(self):
        return super().view_list()

    def view_add(self):
        query_p = DBSession.query(Partner.id, Partner.name).order_by(Partner.name)
        options = [(p.id, p.name) for p in query_p.all()]
        
        schema = self.ListSchema().bind(request=self.request)
        schema['partner_id'].widget.values = options
        
        form = Form(schema, buttons=('save', 'cancel'))
        resources = form.get_widget_resources()
        
        if self.request.POST:
            if 'save' in self.request.POST:
                controls = self.request.POST.items()
                try:
                    appstruct = form.validate(controls)
                    
                    new_row = self.table()
                    for key in appstruct:
                        setattr(new_row, key, appstruct[key])
                    
                    DBSession.add(new_row)
                    DBSession.flush() 
                    
                    # Ganti self.route_list() dengan ini:
                    return self.redirect_list()
                except ValidationFailure as e:
                    return {
                        "form": e.render(), 
                        "scripts": resources['js'], 
                        "styles": resources['css'], 
                        "title": "Tambah Order"
                    }
            else:
                return self.redirect_list()

        return {
            "form": form.render(),
            "scripts": resources['js'],
            "styles": resources['css'],
            "title": "Tambah Order Baru"
        }

    def view_read(self):
        return {"title": "Detail Order", "scripts": [], "styles": []}

    def view_checkout(self):
        return {"title": "Checkout Order", "scripts": [], "styles": []}

    def view_act(self):
        return super().view_act()