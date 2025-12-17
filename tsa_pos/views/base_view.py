import datetime
import logging
import colander
import deform

from deform import widget
from pyramid.httpexceptions import HTTPFound
from pyramid.csrf import new_csrf_token, get_csrf_token
from pyramid.exceptions import HTTPNotFound
from datatables import ColumnDT, DataTables

from ..detable import DeTable
from ..tools import *
from ..models import DBSession
from ..widgets import tsa_widget
from ..i18n import _
_logging = logging.getLogger(__name__) # error, warning, info, debug

class MemoryTmpStore(dict):
    """ Instances of this class implement the
    :class:`defWorm.interfaces.FileUploadTempStore` interface"""

    def preview_url(self, uid):
        return None

MEM_TMP_STORE = MemoryTmpStore()

class UploadSchema(colander.Schema):
    upload = colander.SchemaNode(
        deform.FileData(),
        widget=widget.FileUploadWidget(MEM_TMP_STORE),
        title='Unggah')


class CSRFSchema(colander.Schema):
    def after_bind(self, schema, kwargs):
        request = kwargs["request"]
        csrf_token = get_csrf_token(request)
        if not csrf_token:
            csrf_token = new_csrf_token(request)

        self["csrf_token"] = colander.SchemaNode(
            colander.String(), widget=widget.HiddenWidget(),
            default=csrf_token
        )

class CreateSchema(colander.MappingSchema):
    pass


class UpdateSchema(CreateSchema):
    pass

class ListSchema(UpdateSchema):
    pass

class ReadSchema(UpdateSchema):
    def after_bind(self, node, kw):
        for child in node.children:
            child.widget.readonly = True
            child.missing = colander.drop

class BaseViews(object):
    def __init__(self, request):
        self.request = request
        self.home = request.route_url('home')
        self.db_session = DBSession
        self.table = None  # Default table, must be overridden
        self.CreateSchema = CreateSchema  # Default schema, must be overridden
        self.ReadSchema = ReadSchema  # Default read schema, must be overridden
        self.UpdateSchema = UpdateSchema  # Default schema, must be overridden
        self.is_object = False
        # datatable settings
        self.ListSchema = UpdateSchema  # Default list schema, must be overridden
        self.list_route_name = ''  # Default list route name, must be overridden
        self.allow_view=True
        self.allow_add=True
        self.allow_edit=True
        self.allow_delete=True
        self.allow_post=False
        self.allow_unpost=False
        self.allow_check=False
        self.check_field = False
        self.state_save= False
        self.server_side = True
        self.list_url = ''
        self.list_route = ''
        self.action_suffix = '/grid/act'
        self.html_buttons = ''
        self.scroll_y = False
        self.scroll_x = False
        self.new_buttons = None
        self.list_col_defs = []
        self.columns = []
        self.list_report = (btn_csv, btn_pdf)
        self.list_buttons = (btn_add,)
        self.list_upload = (btn_upload,)
        self.column_filter = False
        
        # end of datatable settings
        self.bindings = {}
        
    def get_bindings(self):
        return {}

    # datatable start
    def view_list(self, **kwargs):
         # Logic to fetch all data from the database goes here
        """
        custom:
            allow_view = kwargs.get("allow_view", self.allow_view)
            allow_edit = kwargs.get("allow_edit", self.allow_edit)
            allow_delete = kwargs.get("allow_delete", self.allow_delete)
            allow_post = kwargs.get("allow_post", self.allow_post)
            allow_unpost = kwargs.get("allow_unpost", self.allow_unpost)
            allow_check = kwargs.get("allow_check", self.allow_check)
            state_save = kwargs.get("state_save", self.state_save)
            filter_columns = kwargs.get("filter_columns", self.filter_columns)
            server_side = kwargs.get("server_side", self.server_side)
            new_buttons
            list_url
            action_suffix
            html_buttons
        """

        allow_view = kwargs.pop("allow_view", self.allow_view)
        allow_edit = kwargs.pop("allow_edit", self.allow_edit)
        allow_delete = kwargs.pop("allow_delete", self.allow_delete)
        allow_post = kwargs.pop("allow_post", self.allow_post)
        allow_unpost = kwargs.pop("allow_unpost", self.allow_unpost)
        allow_check = kwargs.pop("allow_check", self.allow_check)
        check_field = kwargs.pop("check_field", self.check_field)

        state_save = kwargs.pop("state_save", self.state_save)
        filter_columns = kwargs.pop("filter_columns", self.filter_columns)
        server_side = kwargs.pop("server_side", self.server_side)
        new_buttons = kwargs.pop("new_buttons", self.new_buttons)
        is_object = kwargs.pop("is_object", self.is_object)
        list_url = kwargs.pop("list_url", self.list_url)
        action_suffix = kwargs.pop("action_suffix", self.action_suffix)
        list_schema = kwargs.pop("list_schema", self.ListSchema)
        scroll_y = kwargs.pop("scroll_y", self.scroll_y)
        scroll_x = kwargs.pop("scroll_x", self.scroll_x)
        html_buttons = kwargs.pop("html_buttons", self.html_buttons)
        parent = kwargs.pop("parent", None)

        if list_schema:
            if parent:
                action_suffix += f'?parent_id={parent.id}'

            schema = self.ListSchema()
            if "bindings" in kwargs and kwargs["bindings"]:
                bindings = kwargs["bindings"]
            elif self.bindings:
                bindings = self.bindings
            else:
                bindings = self.get_bindings()
                
            schema = schema.bind(request=self.request, **bindings)

            if not new_buttons:
                new_buttons = self.new_buttons

            if not list_url and self.list_route:
                list_url = self.request.route_url(self.list_route)
            else:
                if list_url[:4] != 'http':
                    list_url = f"/{list_url}".replace("//", "/")
                    list_url = self.home + list_url

            table = DeTable(schema,
                            action=list_url,
                            action_suffix=action_suffix,
                            buttons=self.list_buttons,
                            request=self.request,
                            allow_view=allow_view,
                            allow_edit=allow_edit,
                            allow_delete=allow_delete,
                            allow_post=allow_post,
                            allow_unpost=allow_unpost,
                            allow_check=allow_check,
                            check_field=check_field,
                            state_save=state_save,
                            new_buttons=new_buttons,
                            filter_columns=filter_columns,
                            server_side=server_side,
                            scroll_y=scroll_y,
                            scroll_x=scroll_x,
                            html_buttons=html_buttons,
                            **kwargs
                            )
            resources = table.get_widget_resources()
            if is_object:
                return dict(form=table, scripts="", css=resources["css"],
                            js=resources["js"])

            return dict(form=table.render(), scripts="", css=resources["css"],
                        js=resources["js"])

        arg = kwargs and kwargs or {}
        arg.update(url=self.list_url, col_defs=self.list_col_defs,
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        buttons=self.list_buttons)
=======
=======
>>>>>>> 0010e7b (update invoice)
                #    cols=self.list_cols, 
=======
>>>>>>> 84c5a9a (update invoice)
                   buttons=self.list_buttons)
>>>>>>> 6c50c3f (feat: Add multiple database migrations for product, accounting, permissions, partner, invoice, wilayah, and payment models)
=======
        buttons=self.list_buttons)
>>>>>>> 55d395b (base views)
=======
=======
>>>>>>> 0010e7b (update invoice)
                #    cols=self.list_cols, 
=======
>>>>>>> 84c5a9a (update invoice)
                   buttons=self.list_buttons)
>>>>>>> 6c50c3f (feat: Add multiple database migrations for product, accounting, permissions, partner, invoice, wilayah, and payment models)
        return arg


    def view_act(self, **kwargs):
        #Standard Action grid csv pdf dan next_act
        url_dict = self.request.matchdict
        if url_dict['act'] == 'grid':
            return self.get_list(**kwargs)

        elif url_dict['act'] == 'csv':
            return self.csv_response(**kwargs)

        elif url_dict['act'] == 'pdf':
            return self.pdf_response(**kwargs)

        else:
            return self.next_act(**kwargs)
        

    def get_list(self, **kwargs):
        """
        parameter
        list_schema optional
        list_join callback
        list_filter callback
        """
        url = []
        select_list = {}
        list_schema = kwargs.get("list_schema", self.ListSchema)

        if not self.columns:
            columns = []
            for d in list_schema():
                global_search = True
                search_method = hasattr(d, "search_method") \
                    and getattr(d, "search_method") or "string_contains"
                if hasattr(d, "global_search"):
                    if d.global_search == False:
                        global_search = False

                if hasattr(d, "field"):
                    if type(d.field) == str:
                        columns.append(
                            ColumnDT(getattr(self.table, d.field),
                                     mData=d.name,
                                     global_search=global_search,
                                     search_method=search_method))
                    else:
                        columns.append(
                            ColumnDT(d.field, mData=d.name,
                                     global_search=global_search,
                                     search_method=search_method
                                     ))
                else:
                    columns.append(
                        ColumnDT(getattr(self.table, d.name),
                                 mData=d.name,
                                 global_search=global_search,
                                 search_method=search_method))
                if hasattr(d, "widget"):
                    if d.widget:
                        _logging.debug(d.widget)
                        if type(d.widget) is deform.widget.SelectWidget:
                            select_list[d.name] = d.widget.values

                if hasattr(d, "url"):
                    url.append(d.name)
        else:
            columns = self.columns

        # Get Data From Database
        query = self.db_session.query().select_from(self.table)
        list_join = kwargs.get('list_join', self.list_join)
        query = list_join(query, **kwargs)
        list_filter = kwargs.get('list_filter', self.list_filter)
        query = list_filter(query, **kwargs)
        # End Get Data From Database

        row_table = DataTables(self.request.GET, query, columns)
        result = row_table.output_result()
        data = result and result.get("data") or {}
        for res in data:
            for k in res:
                if k in select_list.keys():
                    vals = select_list[k]
                    for r in vals:
                        if r and str(r) == str(res[k]):
                            res[k] = vals[r]
        #     for k, v in d.items():
        #         if k in url and v:
        #             link = "/".join([self.home, nik_url, v])
        #             d[k] =f'<a href="{link}" target="_blank">View</a>'
        return result

    def filter_columns(self, query, **kwargs):
        return query
    
    def list_join(self, query, **kwargs):
        return query

    def list_filter(self, query, **kwargs):
        return query

    def next_act(self, **kwargs):
        # url_dict = self.request.matchdict
        raise HTTPNotFound

    def pdf_response(self, **kwargs):
        from opensipkd.base.tools.report import jasper_export
        filename = jasper_export(self.report_file)
        return file_response(self.request, filename=filename[0])

    def csv_response(self, **kwargs):
        query = self.table.query_register()
        row = query.first()
        header = row._mapping.keys()
        rows = [list(item) for item in query.all()]
        filename = f"{get_random_string(16)}.csv"
        value = {
            'header': header,
            'rows': rows,
        }
        return csv_response(self.request, value, filename)

    # data table end 
    def save(self, values, row=None):
        now = datetime.datetime.now()
        if not row:
            row = self.table()
            if hasattr(row, 'create_uid'):
                row.create_uid = self.request.user.id
            if hasattr(row, 'status'):
                row.status = 1  # Default to active status
            if hasattr(row, 'created'):
                row.created = now
        else:
            if hasattr(row, 'update_uid'):
                row.update_uid = self.request.user.id
            if hasattr(row, 'updated'):
                row.updated = now

        for key, val in values.items():
            if hasattr(row, key):
                setattr(row, key, val)

        self.db_session.add(row)
        self.db_session.flush()
        row = self.after_save(row, values)
        return row
    
    def after_save(self, row, values):
        return row

    def view_create(self):
        form = self.get_form(self.CreateSchema, buttons=('save', 'cancel'))

        if self.request.POST:
            if 'save' in self.request.POST:
                controls = self.request.POST.items()
                try:
                    appstruct = form.validate(controls)
                    self.save(appstruct)
                    self.request.session.flash(_('Data added successfully!'))
                except deform.ValidationFailure as e:
                    return {'form': e.render(), "scripts": ""}

            return HTTPFound(location=self.request.route_url(self.list_route))

        rendered_form = form.render()
        return {'form': rendered_form, "scripts": ""}
    
    def get_form(self, schema_class, buttons=("cancel", )):
        schema = schema_class(
            validator=self.form_validator, request=self.request, widget=tsa_widget.FormWidget())
        schema = schema.bind(request=self.request)
        form = deform.Form(schema, buttons=buttons, )
        return form
    
    def form_validator(self, form, value):
        id_ = self.request.matchdict.get('id', 0)
        excs = self.table.validator(id_, value, form)
        if excs:
            exc = colander.Invalid(
                form,
                'Kesalahan pada pengisian data.'
            )
            for k, v in excs.items():
                exc[k] = v
            raise exc

    def query_id(self):
        id_ = self.request.matchdict.get('id')
        return self.db_session.query(self.table).filter(self.table.id == id_)

    def view_read(self):
        # Logic to fetch user data from the database goes here
        query = self.query_id()
        row = query.first()
        if not row:
            self.request.session.flash(_('Record not found!'), "error")
            return HTTPFound(location=self.request.route_url(self.list_route))

        form = self.get_form(self.ReadSchema)
        if self.request.POST:
            return HTTPFound(location=self.request.route_url(self.list_route))

        # Pre-fill form with existing user data
        appstruct = self.get_values(row)
        rendered_form = form.render(appstruct, readonly=True)
        return {'form': rendered_form, "scripts": ""}

    def view_update(self):
        # Logic to fetch user data from the database goes here
        query = self.query_id()
        row = query.first()
        if not row:
            self.request.session.flash(_('Record not found!'), "error")
            return HTTPFound(location=self.request.route_url(self.list_route))

        form = self.get_form(self.UpdateSchema, buttons=('save', 'cancel'))
        if self.request.POST:
            if 'save' in self.request.POST:
                controls = self.request.POST.items()
                try:
                    appstruct = form.validate(controls)
                    # Logic to update user in the database goes here
                    user = self.save(appstruct, row)
                    self.request.session.flash('Record updated successfully!')
                except deform.ValidationFailure as e:
                    return {'form': e.render(),  "scripts": ""}

            return HTTPFound(location=self.request.route_url(self.list_route))

        # Pre-fill form with existing user data
        appstruct = self.get_values(row)
        rendered_form = form.render(appstruct)
        return {'form': rendered_form, "scripts": ""}

    def get_values(self, row):
        appstruct = dict(row.__dict__)
        # Remove SQLAlchemy internal state
        appstruct.pop('_sa_instance_state', None)
        return appstruct

    def view_delete(self):
        # Logic to fetch user data from the database goes here
        query = self.query_id()
        row = query.first()
        if not row:
            self.request.session.flash('Record not found!')
            return HTTPFound(location=self.request.route_url(self.list_route))
        if self.request.POST:
            if "delete" in self.request.POST:
                try:
                    query.delete()
                    self.request.session.flash('Record deleted successfully!')
                except Exception as e:
                    self.request.session.flash(
                        'Error deleting user: {}'.format(e))

            return HTTPFound(location=self.request.route_url(self.list_route))

        form = self.get_form(self.ReadSchema, buttons=('delete', 'cancel'))
        app_struct = self.get_values(row)
        form.set_appstruct(app_struct)
        rendered_form = form.render()
        return {'form': rendered_form, "scripts": ""}
