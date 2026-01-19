from deform import widget, Form
import colander

from ..models import InvoiceItems, Product
from . import BaseViews
from ..i18n import _


class ListSchema(colander.Schema):
    id = colander.SchemaNode(
        colander.String(),
        missing=colander.drop,
        title="Action",
        widget=widget.HiddenWidget(),
    )
    invoice_id = colander.SchemaNode(colander.Integer(), title=_("Invoice ID"))
    product_id = colander.SchemaNode(colander.Integer(), title=_("Product ID"))
    qty = colander.SchemaNode(colander.Integer(), title=_("Quantity"))
    price = colander.SchemaNode(colander.Float(), title=_("Price"))
    amount = colander.SchemaNode(colander.Float(), title=_("Amount"))


class CreateSchema(colander.Schema):
    product_id = colander.SchemaNode(
        colander.Integer(),
        title=_("Product"),
        widget=widget.SelectWidget(values=[]),
    )
    qty = colander.SchemaNode(colander.Integer(), title=_("Quantity"))
    price = colander.SchemaNode(colander.Float(), title=_("Price"))
    amount = colander.SchemaNode(colander.Float(), title=_("Amount"))

    def after_bind(self, schema, appstruct):
        products = Product.query().all()
        schema["product_id"].widget.values = [(str(p.id), p.name) for p in products]


class UpdateSchema(CreateSchema):
    invoice_id = colander.SchemaNode(
        colander.Integer(), missing=colander.drop, widget=widget.HiddenWidget()
    )
    product_id = colander.SchemaNode(
        colander.Integer(), missing=colander.drop, widget=widget.HiddenWidget()
    )


class Views(BaseViews):

    def __init__(self, request):
        super().__init__(request)
        self.table = InvoiceItems
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = "invoice-items-list"

        self.list_cols = [
            "invoice_id",
            "product_id",
            "qty",
            "price",
            "amount",
        ]

    def form_validator(self, form, value):
        exc = colander.Invalid(form, _("Kesalahan pada pengisian data."))

        invoice_id = self.request.matchdict.get("invoice_id")
        product_id = value.get("product_id")

        row = (
            self.table.query()
            .filter(
                self.table.invoice_id == invoice_id, self.table.product_id == product_id
            )
            .first()
        )

        if row:
            exc["product_id"] = _("Product sudah ada di invoice ini.")
            raise exc

    # def row2dict(self, row):
    #     return {
    #         "invoice_id": row.invoice_id,
    #         "product_id": row.product_id,
    #         "qty": row.qty,
    #         "price": row.price,
    #         "amount": row.amount,
    #         "DT_RowId": f"{row.invoice_id}-{row.product_id}",
    #     }

    # def create_invoice_item(self):
    #     schema = self.CreateSchema()
    #     form = Form(schema, buttons=("submit",))
    #     request = self.request
    #     if request.method == "POST":
    #         controls = request.POST.items()
    #         try:
    #             appstruct = form.validate(controls)
    #             self.form_validator(form, appstruct)

    #             # Simpan ke database
    #             invoice_item = InvoiceItems(
    #                 invoice_id=int(request.matchdict["invoice_id"]),
    #                 product_id=int(appstruct["product_id"]),
    #                 qty=int(appstruct["qty"]),
    #                 price=float(appstruct["price"]),
    #                 amount=float(appstruct["amount"]),
    #             )
    #             self.db_session.add(invoice_item)
    #             self.db_session.flush()

    #             return {
    #                 "success": True,
    #                 "message": _("Invoice item berhasil ditambahkan"),
    #             }
    #         except colander.Invalid as e:
    #             return {"form": form.render(e)}
    #     return {"form": form.render()}

    # # -------------------------
    # # UPDATE
    # # -------------------------
    # def update_invoice_item(self):
    #     schema = self.UpdateSchema()
    #     form = Form(schema, buttons=("submit",))
    #     request = self.request

    #     invoice_id = int(request.matchdict["invoice_id"])
    #     product_id = int(request.matchdict["product_id"])
    #     item = (
    #         self.table.query()
    #         .filter(
    #             self.table.invoice_id == invoice_id, self.table.product_id == product_id
    #         )
    #         .first()
    #     )

    #     if not item:
    #         return {"error": _("Invoice item tidak ditemukan")}

    #     if request.method == "POST":
    #         controls = request.POST.items()
    #         try:
    #             appstruct = form.validate(controls)
    #             self.form_validator(form, appstruct)

    #             # Update fields
    #             item.qty = int(appstruct["qty"])
    #             item.price = float(appstruct["price"])
    #             item.amount = float(appstruct["amount"])
    #             self.db_session.flush()

    #             return {
    #                 "success": True,
    #                 "message": _("Invoice item berhasil diperbarui"),
    #             }
    #         except colander.Invalid as e:
    #             return {"form": form.render(e)}

    #     # Load current values
    #     form_data = {
    #         "invoice_id": item.invoice_id,
    #         "product_id": item.product_id,
    #         "qty": item.qty,
    #         "price": item.price,
    #         "amount": item.amount,
    #     }
    #     return {"form": form.render(appstruct=form_data)}

    # # -------------------------
    # # DELETE
    # # -------------------------
    # def delete_invoice_item(self):
    #     request = self.request
    #     invoice_id = int(request.matchdict["invoice_id"])
    #     product_id = int(request.matchdict["product_id"])

    #     item = (
    #         self.table.query()
    #         .filter(
    #             self.table.invoice_id == invoice_id, self.table.product_id == product_id
    #         )
    #         .first()
    #     )

    #     if not item:
    #         return {"error": _("Invoice item tidak ditemukan")}

    #     self.db_session.delete(item)
    #     self.db_session.flush()

    #     return {"success": True, "message": _("Invoice item berhasil dihapus")}
