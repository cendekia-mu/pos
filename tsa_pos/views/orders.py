import logging
import colander
from deform import widget
from pyramid.view import view_config
from sqlalchemy import func

from ..models import DBSession, Partner, Orders
from . import BaseViews
from ..i18n import _

log = logging.getLogger(__name__)


# =========================================================
# SCHEMA LIST / DATATABLES
# =========================================================
class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(), missing=colander.drop)
    code = colander.SchemaNode(colander.String(), title=_("Nomor Order"), missing="-")
    name = colander.SchemaNode(colander.String(), title=_("Customer"), missing="-")
    amount = colander.SchemaNode(colander.Float(), title=_("Total"), missing=0)
    order_date = colander.SchemaNode(colander.String(), title=_("Tanggal"), missing="-")
    status = colander.SchemaNode(colander.Integer(), title=_("Status"), missing=0)


# =========================================================
# SCHEMA FORM CREATE / UPDATE
# =========================================================
class OrderSchema(colander.Schema):
    code = colander.SchemaNode(colander.String(), title=_("Kode Order"))
    name = colander.SchemaNode(colander.String(), title=_("Nama Transaksi"), missing="-")
    amount = colander.SchemaNode(colander.Float(), title=_("Total"), missing=0)
    partner_id = colander.SchemaNode(
        colander.Integer(),
        title=_("Partner"),
        widget=widget.SelectWidget(values=[]),
    )

    def after_bind(self, schema, appstruct):
        partners = DBSession.query(Partner).all()
        schema["partner_id"].widget.values = [
            (str(p.id), p.name) for p in partners
        ]


# =========================================================
# VIEWS
# =========================================================
class Views(BaseViews):

    def __init__(self, request):
        super().__init__(request)
        self.table = Orders
        self.ListSchema = ListSchema
        self.CreateSchema = OrderSchema
        self.UpdateSchema = OrderSchema
        self.list_route = "order-list"

    # -----------------------------------------------------
    # QUERY UNTUK DATATABLES
    # -----------------------------------------------------
    def query_data(self):
        query = DBSession.query(
            Orders.id.label("id"),
            Orders.code.label("code"),
            Partner.name.label("name"),
            Orders.amount.label("amount"),
            func.to_char(
                Orders.order_date, 'YYYY-MM-DD'
            ).label("order_date"),
            Orders.status.label("status"),
        ).outerjoin(
            Partner, Partner.id == Orders.partner_id
        )

        self._columns = {
            "code": Orders.code,
            "name": Partner.name,
            "amount": Orders.amount,
            "order_date": Orders.order_date,
            "status": Orders.status,
        }

        return query

    # -----------------------------------------------------
    # AJAX DATATABLES (FINAL – PAKAI grid())
    # -----------------------------------------------------
    @view_config(renderer="json")
    def view_act(self):
        try:
            return self.grid()
        except Exception as e:
            log.exception("DATATABLES ERROR")
            return {
                "data": [],
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "error": str(e),
            }

    # -----------------------------------------------------
    # HALAMAN LIST
    # -----------------------------------------------------
    def view_list(self):
        return super().view_list()
