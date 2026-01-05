import sqlalchemy as sa
import colander
from deform import widget, Form, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from datetime import datetime
from ..models import DBSession, Orders, Partner
from . import BaseViews
from tsa_pos.widgets import tsa_widget 
from tsa_pos.detable import DeTable # Pastikan ini diimport untuk view_list

class CreateSchema(colander.Schema):
    code = colander.SchemaNode(
        colander.String(), 
        title="Kode Order",
        validator=colander.Length(min=1, max=128)
    )
    name = colander.SchemaNode(
        colander.String(), 
        title="Nama/Keterangan", 
        missing='-',
        validator=colander.Length(max=128)
    )
    order_date = colander.SchemaNode(
        colander.DateTime(),
        title="Tanggal Order",
        widget=tsa_widget.BootStrapDateInputWidget()
    )
    est_delivery = colander.SchemaNode(
        colander.DateTime(),
        title="Estimasi Pengiriman",
        missing=None,
        widget=tsa_widget.BootStrapDateInputWidget()
    )
    partner_id = colander.SchemaNode(
        colander.Integer(), 
        title="Partner", 
        widget=widget.SelectWidget(values=[])
    )
    amount = colander.SchemaNode(
        colander.Float(), 
        title="Total Amount", 
        default=0
    )
    status = colander.SchemaNode(
        colander.Integer(),
        title="Status",
        default=1,
        widget=widget.SelectWidget(values=[(1, 'Draft'), (2, 'Posted')])
    )

class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(
        colander.Integer(), 
        missing=colander.drop, 
        widget=widget.HiddenWidget()
    )

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Orders
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema  
        self.list_route = 'order-list'

    def get_partners(self, schema):
        query_p = DBSession.query(Partner.id, Partner.name).order_by(Partner.name)
        schema['partner_id'].widget.values = [(p.id, p.name) for p in query_p.all()]
        return schema

    def view_list(self):
        """Menampilkan tabel daftar order"""
        schema = self.UpdateSchema().bind()
        # Menggunakan DeTable untuk integrasi DataTables
        form = DeTable(schema, action='/order', action_suffix='/grid/act', buttons=('add', 'edit', 'delete'))
        return dict(
            form=form.render(),
            scripts=form.scripts,
            buttons=form.buttons
        )

    def view_act(self):
        """Endpoint JSON untuk DataTables"""
        act = self.request.matchdict.get('act')
        if act == 'grid':
            query = DBSession.query(self.table)
            rows = query.all()
            data = []
            for row in rows:
                data.append({
                    "id": row.id,
                    "code": row.code,
                    "name": row.name,
                    "order_date": row.order_date.strftime('%Y-%m-%d') if row.order_date else '',
                    "amount": row.amount,
                    "status": row.status
                })
            return {
                "draw": int(self.request.params.get('draw', 1)),
                "recordsTotal": len(data),
                "recordsFiltered": len(data),
                "data": data
            }
        return {"error": "Action not found"}

    def view_add(self):
        schema = self.CreateSchema().bind(request=self.request)
        schema = self.get_partners(schema)
        form = Form(schema, buttons=('save', 'cancel'))
        
        if self.request.POST:
            if 'save' in self.request.POST:
                try:
                    appstruct = form.validate(self.request.POST.items())
                    obj = self.table()
                    for key, value in appstruct.items():
                        setattr(obj, key, value)
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
        schema = self.get_partners(schema) # Perbaikan: panggil get_partners, bukan get_parents
        form = Form(schema, buttons=('save', 'cancel'))

        if self.request.POST:
            if 'save' in self.request.POST:
                try:
                    appstruct = form.validate(self.request.POST.items())
                    for key, value in appstruct.items():
                        setattr(row, key, value)
                    return HTTPFound(location=self.request.route_url(self.list_route))
                except ValidationFailure as e:
                    return {"form": e.render(), "title": f"Edit Order: {row.code}"}
            return HTTPFound(location=self.request.route_url(self.list_route))
        
        # Inisialisasi data lama ke dalam form
        values = {c.name: getattr(row, c.name) for c in sa.inspect(row).mapper.column_attrs}
        return {"form": form.render(appstruct=values), "title": f"Edit Order: {row.code}"}