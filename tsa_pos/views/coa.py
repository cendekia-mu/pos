from deform import widget
import colander
from ..models import coa
from . import BaseViews
from ..i18n import _

class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             title="ID",
                             widget=widget.HiddenWidget())
    name = colander.SchemaNode(colander.String(),
                               title="Name")
    code = colander.SchemaNode(colander.String(),
                               title="Code")
    parent_id = colander.SchemaNode(colander.Integer(),
                                    missing=colander.drop,
                                    title="Parent ID",
                                    widget=widget.HiddenWidget())
    status = colander.SchemaNode(colander.Integer(),
                                 title="Status",
                                 validator=colander.OneOf([0, 1]),
                                 widget=widget.SelectWidget(values=[(0, 'Inactive'), (1, 'Active')]))

class CreateSchema(colander.Schema):
    name = colander.SchemaNode(colander.String(),
                               validator=colander.Length(min=3, max=128),
                               title="Name")
    code = colander.SchemaNode(colander.String(),
                               validator=colander.Length(min=1, max=128),
                               title="Code")
    parent_id = colander.SchemaNode(colander.Integer(),
                                    missing=colander.drop,
                                    title="Parent Coa",
                                    widget=widget.SelectWidget(values=[]))
    status = colander.SchemaNode(colander.Integer(),
                                 missing=1,
                                 title="Status",
                                 validator=colander.OneOf([0, 1]),
                                 widget=widget.SelectWidget(values=[(0, 'Inactive'), (1, 'Active')]))

class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             widget=widget.HiddenWidget())

class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = coa 
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema  
        self.ReadSchema = UpdateSchema  
        self.ListSchema = ListSchema
        self.list_route = 'coa-list'  

    def form_validator(self, form, value):
        exc = colander.Invalid(
            form,
            'Kesalahan pada pengisian data.'
        )
        id_ = self.request.matchdict.get('id', 0)

        name = value.get('name')
        if name:
            row = self.table.query().filter(self.table.name == name).first()
            if row and (not id_ or row.id != int(id_)):
                exc["name"] = _(
                    'Name {} already exists.'.format(name))
                raise exc

        code = value.get('code')
        if code:
            row = self.table.query().filter(self.table.code == code).first()
            if row and (not id_ or row.id != int(id_)):
                exc["code"] = _(
                    'Code {} already exists.'.format(code))
                raise exc

        parent_id = value.get('parent_id')
        if parent_id:
            parent = self.table.query().filter(self.table.id == parent_id).first()
            if not parent:
                exc["parent_id"] = _('Parent Coa does not exist.')
                raise exc
            if id_ and int(id_) == parent_id:
                exc["parent_id"] = _('Cannot set self as parent.')
                raise exc