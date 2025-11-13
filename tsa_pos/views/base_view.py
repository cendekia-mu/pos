import colander
import deform
from pyramid.httpexceptions import HTTPFound
from pyramid.csrf import new_csrf_token, get_csrf_token
from deform import widget


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


class ReadSchema(UpdateSchema):
    def after_bind(self, node, kw):
        for child in node.children:
            child.widget.readonly = True
            child.missing = colander.drop

class BaseViews(object):
    def __init__(self, request):
        self.request = request
        self.table = None  # Default table, can be overridden
        self.CreateSchema = CreateSchema  # Default schema, can be overridden
        self.UpdateSchema = UpdateSchema  # Default schema, can be overridden
        self.ReadSchema = ReadSchema  # Default read schema, can be overridden
        self.list_route_name = ''  # Default list route name, can be overridden

    def view_list(self):
        # Logic to fetch all users from the database goes here
        rows = self.table.query().all()
        return {'rows': rows}

    def view_act(self, **kwargs):
        url_dict = self.req.matchdict
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
        list_schema = kwargs.get("list_schema")
        if not list_schema:
            list_schema = self.list_schema and self.list_schema or self.form_list

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
                        log.debug(d.widget)
                        if type(d.widget) is SelectWidget:
                            select_list[d.name] = d.widget.values

                if hasattr(d, "url"):
                    url.append(d.name)
        else:
            columns = self.columns

        query = self.db_session.query().select_from(self.table)
        list_join = kwargs.get('list_join')
        if list_join is not None:
            query = list_join(query, **kwargs)
        else:
            query = self.list_join(query, **kwargs)
        if self.req.user and self.req.user.company_id and hasattr(self.table, "company_id"):
            query = query.filter(
                self.table.company_id == self.req.user.company_id)
        list_filter = kwargs.get('list_filter')
        if list_filter is not None:
            query = list_filter(query, **kwargs)
        else:
            query = self.list_filter(query, **kwargs)

        # log.debug(str(columns))
        # qry = query.add_columns(*[c.sqla_expr for c in columns])
        # log.debug(str(qry))
        row_table = DataTables(self.req.GET, query, columns)
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

    def list_join(self, query, **kwargs):
        return query

    def list_filter(self, query, **kwargs):
        return query

    def next_act(self, **kwargs):
        url_dict = self.req.matchdict
        raise HTTPNotFound

    def pdf_response(self, **kwargs):
        from opensipkd.base.tools.report import jasper_export
        filename = jasper_export(self.report_file)
        return file_response(self.req, filename=filename[0])

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
        return csv_response(self.req, value, filename)


    def save(self, values, row=None):
        if not row:
            row = self.table()

        for key, val in values.items():
            if hasattr(row, key):
                setattr(row, key, val)

        self.request.dbsession.add(row)
        self.request.dbsession.flush()
        return row

    def view_create(self):
        form = self.get_form(self.CreateSchema, buttons=('save', 'cancel'))

        if self.request.POST:
            if 'save' in self.request.POST:
                controls = self.request.POST.items()
                try:
                    appstruct = form.validate(controls)
                    # Logic to add user to the database goes here
                    self.save(appstruct)
                    self.request.session.flash('User added successfully!')
                except deform.ValidationFailure as e:
                    return {'form': e.render()}

            return HTTPFound(location=self.request.route_url(self.list_route_name))

        rendered_form = form.render()
        return {'form': rendered_form}

    def form_validator(self, form, value):
        pass

    def query_id(self):
        id_ = self.request.matchdict.get('id')
        return self.request.dbsession.query(self.table).filter(self.table.id == id_)

    def get_form(self, schema_class, buttons=("cancel", )):
        schema = schema_class(
            validator=self.form_validator, request=self.request)
        schema = schema.bind(request=self.request)
        form = deform.Form(schema, buttons=buttons)
        return form

    def view_read(self):
        # Logic to fetch user data from the database goes here
        query = self.query_id()
        row = query.first()
        if not row:
            self.request.session.flash('Record not found!')
            return HTTPFound(location=self.request.route_url(self.list_route_name))

        form = self.get_form(self.ReadSchema)
        if self.request.POST:
            return HTTPFound(location=self.request.route_url(self.list_route_name))

        # Pre-fill form with existing user data
        appstruct = self.get_values(row)
        rendered_form = form.render(appstruct)
        return {'form': rendered_form}

    def view_update(self):
        # Logic to fetch user data from the database goes here
        query = self.query_id()
        row = query.first()
        if not row:
            self.request.session.flash('User not found!')
            return HTTPFound(location=self.request.route_url('user'))

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
                    return {'form': e.render()}

            return HTTPFound(location=self.request.route_url(self.list_route_name))

        # Pre-fill form with existing user data
        appstruct = self.get_values(row)
        rendered_form = form.render(appstruct)
        return {'form': rendered_form}

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
            return HTTPFound(location=self.request.route_url(self.list_route_name))
        if self.request.POST:
            if "delete" in self.request.POST:
                try:
                    query.delete()
                    self.request.session.flash('Record deleted successfully!')
                except Exception as e:
                    self.request.session.flash(
                        'Error deleting user: {}'.format(e))

            return HTTPFound(location=self.request.route_url(self.list_route_name))

        form = self.get_form(self.ReadSchema, buttons=('delete', 'cancel'))
        app_struct = self.get_values(row)
        form.set_appstruct(app_struct)
        rendered_form = form.render()
        return {'form': rendered_form}
