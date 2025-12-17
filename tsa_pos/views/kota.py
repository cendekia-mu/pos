<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
import colander
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> 2814337 (update kota)
=======
>>>>>>> ed1299d (invoice dan form login)
=======
>>>>>>> ee0465c (Perubahan)
=======
=======
import colander
<<<<<<< HEAD
>>>>>>> ba4e848 (update kota)
>>>>>>> 90e1579 (update kota)
from deform import widget
import colander
from ..models import Kota,Provinsi
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 90e1579 (update kota)
from ..models import Kota, Provinsi
=======
=======
from ..models import Kota, Provinsi
>>>>>>> fb37090 (update kota)
>>>>>>> 2814337 (update kota)
<<<<<<< HEAD
=======
from ..models import Kota, Provinsi
>>>>>>> ed1299d (invoice dan form login)
=======
=======
from ..models import Kota, Provinsi
>>>>>>> fb37090 (update kota)
>>>>>>> 2814337 (update kota)
=======
from ..models import Kota, Provinsi
>>>>>>> ed1299d (invoice dan form login)
=======
>>>>>>> 90e1579 (update kota)
from . import BaseViews
from ..i18n import _


class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(),
                                missing=colander.drop,
                                title="Action",
                                widget=widget.HiddenWidget(),
    )
    name = colander.SchemaNode(colander.String())


class CreateSchema(colander.Schema):
    # Define your schema fields here
    name = colander.SchemaNode(colander.String(),
                                validator=colander.Length(min=3, max=50)
    )
    provinsi_id = colander.SchemaNode(colander.Integer(),
                                widget=widget.SelectWidget(values=[]),
    )

    def after_bind(self, schema, appstruct):
        # Populate category_id choices
        provinsi = Provinsi.query().all()
        schema["provinsi_id"].widget.values = [
            (str(prov.id), prov.name) for prov in provinsi
        ]


class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(),
                                missing=colander.drop,
                                widget=widget.HiddenWidget()
    )
    provinsi_id = colander.SchemaNode(colander.Integer(),
                                widget=widget.SelectWidget(values=[]),
    )

    def after_bind(self, schema, appstruct):
        # Populate category_id choices
        provinsi = Provinsi.query().all()
        schema["provinsi_id"].widget.values = [
            (str(prov.id), prov.name) for prov in provinsi
        ]


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Kota
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = "kota-list"

    def form_validator(self, form, value):
        exc = colander.Invalid(form, "Kesalahan pada pengisian data.")
        id_ = self.request.matchdict.get("id", 0)

        # Validate unique name
        name = value.get("name")
        row = self.table.query().filter(self.table.name == name).first()
        if row and (not id_ or row.id != int(id_)):
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 2814337 (update kota)
            exc["name"] = _("Name {} already exists.".format(name))
            raise exc

    def list_join(self, query, **kwargs):

        return query.join(Provinsi, Provinsi.id == Kota.provinsi_id )
        return query.join(Provinsi, Provinsi.id == Kota.provinsi_id )
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 90e1579 (update kota)
        return query.join(Provinsi, Provinsi.id == Kota.provinsi_id)

=======
        
>>>>>>> d670049 (WIP: Perubahan lokal sebelum pull dari main)
=======
        return query.join(Provinsi, Provinsi.id == Kota.provinsi_id)

>>>>>>> 2814337 (update kota)
<<<<<<< HEAD
=======
            exc["name"] = _(
                'Name {} already exists.'.format(name))
<<<<<<< HEAD
            raise exc
<<<<<<< HEAD
>>>>>>> ee0465c (Perubahan)
=======
    def list_join(self, query, **kwargs):

        return query.join(Provinsi, Provinsi.id == Kota.provinsi_id )
        return query.join(Provinsi, Provinsi.id == Kota.provinsi_id )
        
>>>>>>> d670049 (WIP: Perubahan lokal sebelum pull dari main)
=======
        return query.join(Provinsi, Provinsi.id == Kota.provinsi_id)

>>>>>>> 2814337 (update kota)
=======
            raise exc
>>>>>>> ee0465c (Perubahan)
=======
>>>>>>> 90e1579 (update kota)
