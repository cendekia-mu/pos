from deform import widget
import colander
from ..models import Product, ProductCategory
from . import BaseViews
from ..i18n import _


class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             title="Action",
                             widget=widget.HiddenWidget())
    name = colander.SchemaNode(colander.String())
    stock = colander.SchemaNode(colander.Integer(), missing=colander.drop   ,
                                widget=widget.TextInputWidget(readonly=True),)
    min_stock = colander.SchemaNode(colander.Integer(),)
    selleable = colander.SchemaNode(colander.Integer(),
                                    widget=widget.CheckboxWidget(true_val="1", false_val="0"),)

    category_id = colander.SchemaNode(colander.Integer(),
                                      widget=widget.SelectWidget(values=[]),)   

    def after_bind(self, schema, appstruct):
        # Populate category_id choices
        categories = ProductCategory.query().all()
        schema['category_id'].widget.values = [
            (str(cat.id), cat.name) for cat in categories
        ]

class CreateSchema(ListSchema):
    # Define your schema fields here
    def after_bind(self, schema, appstruct):
        super().after_bind(schema, appstruct)
        del schema['id']  # Remove id field for creation

class UpdateSchema(ListSchema):
    pass

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Product
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = 'product-list'

    def form_validator(self, form, value):
        exc = colander.Invalid(
            form,
            'Kesalahan pada pengisian data.'
        )
        id_ = self.request.matchdict.get('id', 0)

        # Validate unique name
        name = value.get('name')
        row = self.table.query().filter(self.table.name == name).first()
        if row and (not id_ or row.id != int(id_)):
            exc["name"] = _(
                'Name {} already exists.'.format(name))
            raise exc
