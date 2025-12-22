import sqlalchemy as sa
import colander
from deform import widget, Form, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from ..models import DBSession, Orders, Partner
from . import BaseViews
from ..i18n import _

class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             title="ID",
                             widget=widget.HiddenWidget())
    code = colander.SchemaNode(colander.String(), title="Kode Order")
    order_date = colander.SchemaNode(colander.String(), title="Tgl. Order")
    amount = colander.SchemaNode(colander.Integer(), title="Total")

class CreateSchema(colander.Schema):
    code = colander.SchemaNode(colander.String(), title="Kode Order")
    name = colander.SchemaNode(colander.String(), title="Keterangan", missing='-')
    order_date = colander.SchemaNode(
        colander.Date(),
        title="Tanggal Order",
        widget=widget.DateInputWidget(attributes={'readonly':'readonly'}))
    est_delivery = colander.SchemaNode(
        colander.Date(),
        title="Estimasi Pengiriman",
        missing=colander.drop,
        widget=widget.DateInputWidget(attributes={'readonly':'readonly'}))
    partner_id = colander.SchemaNode(colander.Integer(), title="Partner", widget=widget.SelectWidget())
    amount = colander.SchemaNode(colander.Float(), title="Total Amount", default=0)
    status = colander.SchemaNode(
        colander.Integer(),
        title="Status",
        default=1,
        widget=widget.SelectWidget(values=[('1', 'Draft'), ('2', 'Posted')]))

class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(), missing=colander.drop, widget=widget.HiddenWidget())

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Orders
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema  
        self.ListSchema = ListSchema
        self.list_route = 'order-list'

    def view_act(self):
        """Query Data Manual (Tanpa library DataTable)"""
        params = self.request.params
        draw = int(params.get('draw', 1))
        start = int(params.get('start', 0))
        length = int(params.get('length', 10))
        search = params.get('search[value]', '')

        query = DBSession.query(self.table)
        if search:
            query = query.filter(Orders.code.ilike(f'%{search}%'))

        records_total = query.count()
        rows = query.offset(start).limit(length).all()

        data = []
        for row in rows:
            data.append({
                "id": row.id,
                "code": row.code,
                "order_date": row.order_date.strftime('%Y-%m-%d') if row.order_date else '',
                "amount": row.amount,
                "status": row.status
            })

        return {
            "draw": draw,
            "recordsTotal": records_total,
            "recordsFiltered": records_total,
            "data": data
        }

    def view_checkout(self):
        """Fungsi Checkout"""
        return {}

    def view_add(self):
        schema = self.CreateSchema().bind(request=self.request)
        query_p = DBSession.query(Partner.id, Partner.name).order_by(Partner.name)
        schema['partner_id'].widget.values = [(str(p.id), p.name) for p in query_p.all()]
        
        form = Form(schema, buttons=('save', 'cancel'))
        if self.request.POST:
            if 'save' in self.request.POST:
                try:
                    appstruct = form.validate(self.request.POST.items())
                    obj = self.table()
                    for key in appstruct:
                        setattr(obj, key, appstruct[key])
                    DBSession.add(obj)
                    return HTTPFound(location=self.request.route_url(self.list_route))
                except ValidationFailure as e:
                    return {"form": e.render(), "title": "Add Order"}
            return HTTPFound(location=self.request.route_url(self.list_route))
        return {"form": form.render(), "title": "Add Order"}

    def view_edit(self):
        id_ = self.request.matchdict.get('id')
        row = DBSession.query(self.table).filter_by(id=id_).first()
        if not row:
            return HTTPFound(location=self.request.route_url(self.list_route))

        schema = self.UpdateSchema().bind(request=self.request)
        query_p = DBSession.query(Partner.id, Partner.name).order_by(Partner.name)
        schema['partner_id'].widget.values = [(str(p.id), p.name) for p in query_p.all()]
        
        form = Form(schema, buttons=('save', 'cancel'))
        if self.request.POST:
            if 'save' in self.request.POST:
                try:
                    appstruct = form.validate(self.request.POST.items())
                    for key in appstruct:
                        setattr(row, key, appstruct[key])
                    return HTTPFound(location=self.request.route_url(self.list_route))
                except ValidationFailure as e:
                    return {"form": e.render(), "title": f"Edit Order: {row.code}"}
            return HTTPFound(location=self.request.route_url(self.list_route))

        values = {c.name: getattr(row, c.name) for c in sa.inspect(row).mapper.column_attrs}
        return {"form": form.render(appstruct=values), "title": f"Edit Order: {row.code}"}

    def view_delete(self):
        id_ = self.request.matchdict.get('id')
        row = DBSession.query(self.table).filter_by(id=id_).first()
        if row:
            DBSession.delete(row)
        return HTTPFound(location=self.request.route_url(self.list_route))