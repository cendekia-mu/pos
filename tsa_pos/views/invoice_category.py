from deform import widget
import colander
from ..models import InvoiceCategory
from . import BaseViews
from ..i18n import _


class ListSchema(colander.Schema):

    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        title="Action",
        widget=widget.HiddenWidget(),
    )

    name = colander.SchemaNode(
        colander.String(),
        title=_("Name"),
    )


class CreateSchema(colander.Schema):

    name = colander.SchemaNode(
        colander.String(),
        title=_("Invoice Category Name"),
        validator=colander.Length(min=1, max=128),
        widget=widget.TextInputWidget(),
    )


class UpdateSchema(CreateSchema):

    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        widget=widget.HiddenWidget(),
    )


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = InvoiceCategory
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = "invoice-category-list"

    def form_validator(self, form, value):
        exc = colander.Invalid(form, "Kesalahan pada pengisian data.")
        id_ = self.request.matchdict.get("id", 0)

        # Validate unique name
        name = value.get("name")
        row = self.table.query().filter(self.table.name == name).first()
        if row and (not id_ or row.id != int(id_)):
            exc["name"] = _("Name {} already exists.".format(name))
            raise exc