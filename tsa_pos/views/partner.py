from dataclasses import field, fields
from math import atan
from deform import widget
import colander
from sqlalchemy import values
from tsa_pos.alembic.versions import bd39e1834c1b_tambah_models_invoice
from tsa_pos.models.wilayah import Provinsi, Kota, Kecamatan
from tsa_pos.views import kecamatan, provinsi
from tsa_pos.widgets import tsa_widget
from ..models import Partner
from . import BaseViews
from ..i18n import _


class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.String(),
                                 missing=colander.drop,
                                 title="Action",
                                 # Untuk tombol/link aksi
                                 widget=widget.TextInputWidget(readonly=True))
    kode = colander.SchemaNode(colander.String(),
                               title="Kode")
    name = colander.SchemaNode(colander.String(),
                               title="Nama")
    is_vendor = colander.SchemaNode(colander.Boolean(),
                                widget=widget.CheckboxWidget(),
                                title="Is Vendor")
    is_customer = colander.SchemaNode(colander.Boolean(),
                                widget=widget.CheckboxWidget(),
                                title="Is Customer")
    provinsi_id = colander.SchemaNode(colander.String(),
                                title="Provinsi",
                                field=Provinsi.name)
    kota_id = colander.SchemaNode(colander.String(),
                                title="Kota",
                                field=Kota.name)
    kecamatan_id = colander.SchemaNode(colander.String(),
                                title="Kecamatan",
                                field=Kecamatan.name)
    kelurahan = colander.SchemaNode(colander.String(),
                                title="Kelurahan")
    balance = colander.SchemaNode(colander.Decimal(),
                                  title="Balance")

class CreateSchema(colander.Schema):
    kode = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=1, max=20))
    name = colander.SchemaNode(colander.String(),
                               validator=colander.Length(min=3, max=50))
    is_vendor = colander.SchemaNode(colander.Integer(),
                                    title="Is Vendor",
                                    widget=widget.CheckboxWidget(
                                        true_val='1', false_val='0'),
                                    default=0)
    is_customer = colander.SchemaNode(colander.Integer(),
                                      title="Is Customer",
                                      widget=widget.CheckboxWidget(
                                          true_val='1', false_val='0'),
                                      default=1)
    address_1 = colander.SchemaNode(colander.String(),
                                    validator=colander.Length(min=1, max=100),
                                    title="Alamat 1",
                                    # Menggunakan TextAreaWidget berdasarkan spesifikasi "Alamat" sebagai Textarea
                                    widget=widget.TextAreaWidget())
    address_2 = colander.SchemaNode(colander.String(),
                                    missing=colander.drop,
                                    title="Alamat 2",
                                    widget=widget.TextAreaWidget())  # Menggunakan TextAreaWidget untuk konsistensi
    kelurahan = colander.SchemaNode(colander.String(),
                                    validator=colander.Length(min=1, max=50),
                                    title="Kelurahan")
    provinsi_id = colander.SchemaNode(
        colander.Integer(),
        oid="provinsi_id",
        widget=tsa_widget.Select2Widget(
            values=[],
            slave_id='kota_id',
            slave_url='',),
        title="Provinsi")
    kota_id = colander.SchemaNode(
        colander.Integer(),
        oid="kota_id",
        widget=tsa_widget.Select2Widget(
            values=[],
            slave_id='kecamatan_id',
            slave_url='',),
        title="Kota")
    kecamatan_id = colander.SchemaNode(
        colander.Integer(),
        oid="kecamatan_id",
        widget=widget.Select2Widget(
            values=[]),
            title="Kecamatan")
    
    balance = colander.SchemaNode(
        colander.Decimal(),
        oid="balance")
        

    def after_bind(self, schema, kw):
        # Populate provinsi_id choices
        request = kw.get('request')
        provinsis = Provinsi.query()
        provinsi_choices = [(str(prov.id), prov.name) for prov in provinsis]
        provinsi_choices.insert(0, ('', 'Pilih Provinsi...'))
        schema['provinsi_id'].widget.values = provinsi_choices
        kota_url = request.route_url('partner-act', act="kota")+"?provinsi_id="
        schema['provinsi_id'].widget.slave_url = kota_url

        kecamatan_url = request.route_url(
            'partner-act', act="kecamatan")+"?kota_id="
        schema['kota_id'].widget.slave_url = kecamatan_url

    

    # balance = colander.SchemaNode(colander.Decimal(),
    #                               default=0.0,
    #                               title="Balance (Rupiah)")  # Ditambahkan "(Rupiah)" untuk menunjukkan ini untuk pembayaran dalam rupiah


class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             widget=widget.HiddenWidget())


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = Partner
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema
        self.ReadSchema = UpdateSchema  # Asumsi ReadSchema sama dengan UpdateSchema
        self.ListSchema = ListSchema
        self.list_route = 'partner-list'

    def form_validator(self, form, value):
        exc = colander.Invalid(
            form,
            'Kesalahan pada pengisian data.'
        )
        id_ = self.request.matchdict.get('id', 0)

        # Validate unique kode
        kode = value.get('kode')
        if kode:
            row = self.table.query().filter(self.table.kode == kode).first()
            if row and (not id_ or row.id != int(id_)):
                exc["kode"] = _(
                    'Kode {} already exists.'.format(kode))
                raise exc

        # Validate unique name
        name = value.get('name')
        if name:
            row = self.table.query().filter(self.table.name == name).first()
            if row and (not id_ or row.id != int(id_)):
                exc["name"] = _(
                    'Name {} already exists.'.format(name))
                raise exc

    # # Metode tambahan untuk list view, jika diperlukan (misalnya untuk menggabungkan data lokasi dan tipe)
    # def list_view(self):
    #     # Logika untuk mengambil data dan menggabungkan field seperti location dan type
    #     # Contoh: Gabungkan alamat menjadi satu string untuk location
    #     # Gabungkan is_vendor dan is_customer menjadi string tipe
    #     # Ini bisa dilakukan di query atau di template
    #     pass

    def next_act(self, **kwargs):
        act = self.request.matchdict.get('act', 'list')
        if act == 'kota':
            provinsi_id = self.request.params.get('provinsi_id')
            kotas = Kota.query().filter(Kota.provinsi_id == provinsi_id).all()
            results = {str(kota.id): kota.name for kota in kotas}
            # results[""] = "Pilih Kota..."
            return results
            # return self.json_response({'results': results})
        elif act == 'kecamatan':
            kota_id = self.request.params.get('kota_id')
            kecamatans = Kecamatan.query().filter(
                Kecamatan.kota_id == kota_id).all()
            results = {str(kec.id): kec.name for kec in kecamatans}
            # results[""] = "Pilih Kecamatan..."

            return results

        return super().next_act(**kwargs)
    
    def list_join(self, query):
        return query.\
            outerjoin(Provinsi, Provinsi.id == Partner.provinsi_id).\
            outerjoin(Kota, Kota.id == Partner.kota_id).\
            outerjoin(Kecamatan, Kecamatan.id == Partner.kecamatan_id)
    
