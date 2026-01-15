from deform import widget
import colander

from ..models import ReturnsCategory
from . import BaseViews
from ..i18n import _


# =====================================================
# CREATE / UPDATE SCHEMA
# =====================================================
class CreateSchema(colander.Schema):

    name = colander.SchemaNode(
        colander.String(),
        title='Category Name',
        validator=colander.Length(min=1, max=128)
    )


# =====================================================
# LIST SCHEMA
# =====================================================
class ListSchema(colander.Schema):

    id = colander.SchemaNode(colander.Integer())
    name = colander.SchemaNode(colander.String())


# =====================================================
# UPDATE SCHEMA
# =====================================================
class UpdateSchema(CreateSchema):

    id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
        widget=widget.HiddenWidget()
    )


# =====================================================
# VIEWS
# =====================================================
class Views(BaseViews):

    def __init__(self, request):
        super().__init__(request)
        self.table = ReturnsCategory
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = 'return-category-list'

    # --------------------------------------------------
    # VALIDATOR
    # --------------------------------------------------
    def form_validator(self, form, value):
        exc = colander.Invalid(form, _('Invalid form input.'))
        id_ = self.request.matchdict.get('id')

        if value.get('name'):
            q = self.table.query.filter_by(name=value['name'])
            if id_:
                q = q.filter(self.table.id != int(id_))
            if q.first():
                exc['name'] = _('Category already exists.')
                raise exc
