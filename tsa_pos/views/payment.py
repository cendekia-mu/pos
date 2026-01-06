import colander
from deform import widget

from ..models import Payment
from . import BaseViews
from ..i18n import _

class ListSchema(colander.Schema):
    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        title="id",
        widget=widget.HiddenWidget(),
    )

    amount = colander.SchemaNode(
        colander.Float(),
        title="Amount",
    )

    description = colander.SchemaNode(
        colander.String(),
        missing="",
        title="Description",
    )
    


class CreateSchema(colander.Schema):
    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        title="id",
        widget=widget.HiddenWidget(),
    )

    amount = colander.SchemaNode(
        colander.Float(),
        title="Amount",
        widget=widget.TextInputWidget(css_class="form-control"),
    )

    description = colander.SchemaNode(
        colander.String(),
        title="Description",
        missing="",
        widget=widget.TextAreaWidget(rows=3, css_class="form-control"),
    )


    def after_bind(self, schema, appstruct):
        """
        Dipanggil setelah schema dibind ke request.
        Cocok untuk set default / widget behaviour.
        """
        # default amount
        if appstruct is None:
            schema["amount"].default = 0


class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        widget=widget.HiddenWidget(),
    )

    # def after_bind(self, schema, appstruct):
    #     """
    #     after_bind khusus update
    #     """
    #     # panggil after_bind parent
    #     super().after_bind(schema, appstruct)

    #     # contoh: disable amount saat edit
    #     schema["amount"].widget.readonly = True


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Payment
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = "payment-list"

    def form_validator(self, form, value):
        exc = colander.Invalid(form, "Kesalahan pada pengisian data.")

        amount = value.get("amount")
        if amount is not None and amount <= 0:
            exc["amount"] = _("Amount must be greater than 0")
            raise exc