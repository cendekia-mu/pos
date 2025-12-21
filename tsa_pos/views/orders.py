import sqlalchemy as sa
import colander
import json
from deform import widget, Form, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from ..models import DBSession, Orders, Partner
from . import BaseViews
from ..i18n import _

# Bypass library datatables agar server tidak crash jika library belum terpasang
try:
    from sqlalchemy_datatables import DataTable
except ImportError:
    DataTable = None

# 1. SCHEMA UNTUK TAMPILAN TABEL
class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             title="ID",
                             widget=widget.HiddenWidget())
    code = colander.SchemaNode(colander.String(), title="Kode Order")
    order_date = colander.SchemaNode(colander.String(), title="Tgl. Order")
    amount = colander.SchemaNode(colander.Integer(), title="Total")

# 2. SCHEMA UNTUK FORM TAMBAH
class CreateSchema(colander.Schema):
    code = colander.SchemaNode(
        colander.String(),
        title="Kode Order",
        validator=colander.Length(min=3, max=50))
    
    order_date = colander.SchemaNode(
        colander.Date(),
        title="Tanggal Order")
    
    partner_id = colander.SchemaNode(
        colander.Integer(),
        title="Partner",
        widget=widget.SelectWidget())

    amount = colander.SchemaNode(
        colander.Integer(),
        title="Total Amount",
        default=0)
    
    status = colander.SchemaNode(
        colander.Integer(),
        title="Status",
        default=1,
        widget=widget.SelectWidget(values=[(1, 'Draft'), (2, 'Posted')]))

# 3. SCHEMA UNTUK FORM EDIT
class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             widget=widget.HiddenWidget())

# 4. CONTROLLER / VIEWS
class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Orders
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema  
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = 'order-list'
        # Kolom yang akan ditampilkan di DataTables
        self.columns = [Orders.id, Orders.code, Orders.order_date, Orders.amount]

    def view_act(self):
        """Fungsi DataTables Tanpa Library Eksternal"""
        # 1. Ambil parameter pencarian dan paging dari DataTables
        params = self.request.params
        draw = int(params.get('draw', 1))
        start = int(params.get('start', 0))
        length = int(params.get('length', 10))
        search_value = params.get('search[value]', '')

        # 2. Query dasar
        query = DBSession.query(self.table)

        # 3. Fitur Pencarian (Opsional: jika user mengetik di kotak search)
        if search_value:
            query = query.filter(
                sa.or_(
                    Orders.code.ilike(f'%{search_value}%'),
                    # Tambahkan kolom lain jika ingin bisa dicari
                )
            )

        # 4. Hitung total data
        records_total = query.count()

        # 5. Paging (Limit & Offset)
        rows = query.offset(start).limit(length).all()

        # 6. Susun data ke format JSON
        data = []
        for row in rows:
            data.append({
                "id": row.id,
                "code": row.code,
                # Pastikan tanggal diubah ke string agar tidak error JSON
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

    def view_add(self):
        """Form Tambah Data"""
        schema = self.CreateSchema().bind(request=self.request)
        # Mengisi dropdown Partner secara dinamis
        query_p = DBSession.query(Partner.id, Partner.name).order_by(Partner.name)
        schema['partner_id'].widget.values = [(p.id, p.name) for p in query_p.all()]
        
        form = Form(schema, buttons=('save', 'cancel'))
        if self.request.POST:
            if 'save' in self.request.POST:
                controls = self.request.POST.items()
                try:
                    appstruct = form.validate(controls)
                    obj = self.table()
                    for key in appstruct:
                        setattr(obj, key, appstruct[key])
                    DBSession.add(obj)
                    DBSession.flush()
                    return HTTPFound(location=self.request.route_url(self.list_route))
                except ValidationFailure as e:
                    return {"form": e.render(), "title": "Add Order", "scripts": [], "styles": []}
            return HTTPFound(location=self.request.route_url(self.list_route))
        return {"form": form.render(), "title": "Add Order", "scripts": [], "styles": []}

    def view_edit(self):
        """Form Edit Data"""
        id_ = self.request.matchdict.get('id')
        row = DBSession.query(self.table).filter_by(id=id_).first()
        if not row:
            return HTTPFound(location=self.request.route_url(self.list_route))

        schema = self.UpdateSchema().bind(request=self.request)
        # Mengisi dropdown Partner agar muncul saat edit
        query_p = DBSession.query(Partner.id, Partner.name).order_by(Partner.name)
        schema['partner_id'].widget.values = [(p.id, p.name) for p in query_p.all()]
        
        form = Form(schema, buttons=('save', 'cancel'))
        if self.request.POST:
            if 'save' in self.request.POST:
                controls = self.request.POST.items()
                try:
                    appstruct = form.validate(controls)
                    for key in appstruct:
                        setattr(row, key, appstruct[key])
                    DBSession.flush()
                    return HTTPFound(location=self.request.route_url(self.list_route))
                except ValidationFailure as e:
                    return {"form": e.render(), "title": f"Edit Order: {row.code}", "scripts": [], "styles": []}
            return HTTPFound(location=self.request.route_url(self.list_route))

        # Sinkronisasi data model ke form
        values = {c.name: getattr(row, c.name) for c in sa.inspect(row).mapper.column_attrs}
        return {"form": form.render(appstruct=values), "title": f"Edit Order: {row.code}", "scripts": [], "styles": []}

    def view_delete(self):
        """Menghapus Data"""
        id_ = self.request.matchdict.get('id')
        row = DBSession.query(self.table).filter_by(id=id_).first()
        if row:
            DBSession.delete(row)
            DBSession.flush()
        return HTTPFound(location=self.request.route_url(self.list_route))