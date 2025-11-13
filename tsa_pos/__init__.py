import locale
import os
import tempfile
import datetime
import decimal
import csv
import importlib
from logging import getLogger

from waitress import serve
from pyramid.renderers import JSON
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid_mailer import mailer_factory_from_settings
from pyramid.events import subscriber, BeforeRender
from sqlalchemy.engine import engine_from_config
from .tools import *
from .models import (DBSession, Base, init_model)
from .security import MySecurityPolicy, get_user

_logging = getLogger(__name__)

titles = {}
def init_db(settings):
    engine = engine_from_config(
        settings, 'sqlalchemy.', client_encoding='utf8',
        max_identifier_length=30)  # , convert_unicode=True
    DBSession.configure(bind=engine)
    # LogDBSession.configure(bind=engine)
    Base.metadata.bind = engine
    init_model()

def json_renderer():
    json_r = JSON()
    json_r.add_adapter(datetime.datetime, lambda v,
                       request: format_datetime(v))
    json_r.add_adapter(datetime.date, lambda v, request: dmy(v))
    json_r.add_adapter(decimal.Decimal, lambda v, request: str(v))
    return json_r


def json_rpc():
    json_r = JSON()
    json_r.add_adapter(datetime.datetime, lambda v, request: v.isoformat())
    json_r.add_adapter(datetime.date, lambda v, request: v.isoformat())
    json_r.add_adapter(decimal.Decimal, lambda v, request: str(v))
    return json_r


def get_title(request):
    route_name = request.matched_route.name
    return titles[route_name]

def set_config(settings={}):
    session_factory = session_factory_from_settings(settings)
    config = Configurator(settings=settings,
                          root_factory='tsa_pos.models.auth.RootFactory',
                          session_factory=session_factory)
    config.set_default_csrf_options(require_csrf=False)
    config.set_security_policy(MySecurityPolicy(settings["session.secret"]))
    # config.add_subscriber(add_cors_headers_response_callback, NewRequest)
    # config.add_request_method(get_app_name, 'app_name', reify=True)
    # config.add_request_method(get_menus, 'menus', reify=True)
    # # config.add_request_method(get_host, '_host', reify=True)
    # config.add_request_method(get_host, 'home', reify=True)
    config.add_request_method(get_title, 'title', reify=True)
    # config.add_request_method(get_company, 'company', reify=True)

    config.add_request_method(get_user, 'user', reify=True)
    # config.add_request_method(get_departement, 'departement', reify=True)
    # config.add_request_method(get_ibukota, 'ibukota', reify=True)
    # config.add_request_method(get_address, 'address', reify=True)
    # config.add_request_method(get_address2, 'address2', reify=True)

    #     config.add_request_method(get_modules, 'modules', reify=True)
    # config.add_request_method(has_modules, 'has_modules', reify=True)
    # #     config.add_request_method(thousand, 'thousand', reify=True)
    # #     config.add_request_method(is_devel, 'devel', reify=True)
    # config.add_request_method(google_signin_client_id,
    #                           'google_signin_client_id', reify=True)
    # config.add_request_method(google_signin_client_ids,
    #                           'google_signin_client_ids', reify=True)
    # config.add_request_method(allow_register, 'allow_register', reify=True)
    #     config.add_request_method(disable_responsive, 'disable_responsive',
    #                               reify=True)
    #     config.add_request_method(_get_ini, 'get_ini', reify=True)
    # config.add_request_method(get_params, 'get_params', reify=True)
    #     config.add_request_method(get_csrf_token, 'get_csrf_token', reify=True)

    #     # Penambahan Module Auto Generate Menu
    #     # config.add_request_method(get_module_menus, 'get_module_menus', reify=True)
    #     # config.add_request_method(get_module_submenus, 'get_module_submenus', reify=True)

    #     # config.add_translation_dirs('opensipkd.base:locale/')

    #     partner_files = get_params("partner_files", settings=settings,
    #                                alternate="/tmp/partner")
    #     captcha_files = get_params('captcha_files', settings=settings,
    #                                alternate="/tmp/captcha")

    #     if os.sep != '/':
    #         captcha_files = captcha_files.replace('/', '\\')
    #         partner_files = partner_files.replace('/', '\\')

    #     _logging.info(f"Captcha Files: {captcha_files}")
    #     _logging.info(f"Partner Files: {partner_files}")
    #     if not os.path.exists(captcha_files):
    #         os.makedirs(captcha_files)
    #     if not os.path.exists(partner_files):
    #         os.makedirs(partner_files)

    config.add_static_view('static', 'tsa_pos:static',
                           cache_max_age=3600)

    config.add_static_view('deform_static', 'deform:static')

    #     config.add_static_view(partner_idcard_url,
    #                            get_id_card_folder("/", settings=settings),
    #                            cache_max_age=3600)

    #     config.add_static_view('captcha', captcha_files)
    #     config.add_static_view('partner/files', partner_files)

    config.add_renderer('csv', 'tsa_pos.tools.CSVRenderer')
    config.add_renderer('json', json_renderer())
    config.add_renderer('json_rpc', json_rpc())
    config.registry['mailer'] = mailer_factory_from_settings(settings)

    return config

def _add_view_config(config, paket, route):
    _add_route(config, route)
    if not route.get("func_name"):
        func_name = "".join(route.get("kode").split('-')[-1:])
        route["func_name"] = "_".join(["view", func_name])

    file_name = f"{paket}.{route.get('file_name')}"
    # _logging.debug(f"File Name: {file_name}")
    attr = f"{route.get('func_name')}"
    try:

        class_name = route.get("class_name", None)
        if not file_name:
            _logging.error(f"File not found: {file_name}")
            return
        _views = importlib.import_module(file_name)
        
        if not class_name:
            class_name = "Views"
            
        if not hasattr(_views, class_name):
            _logging.error(
                f"Class {class_name} not found in {file_name}")
            return
        
        views = getattr(_views, class_name)
        template = route.get("template", "form.pt")
        if not template:
            if route.get("func_name") == "view_list":
                template = "list.pt"
            elif route.get("func_name") == "view_act":
                template = "json"
            else:
                template = "form.pt"

        if template != "json":
            template = "tsa_pos:templates/" + template

        params = dict(attr=f"{attr}",
                      route_name=route.get("kode"),
                      renderer=template)
        
        if route.get("permission"):
            params["permission"] = route.get("permission")
        if route.get("csrf"):
            params["require_csrf"] = True
        if route.get("request_method"):
            params["request_method"] = route.get("request_method")
        if route.get("typ")==2:
            params.pop("attr", None)
            params.pop("renderer", None)
            config.add_view(views.as_view(), **params)
        else:
            config.add_view(views, **params)

    except Exception as e:
        _logging.error("Add View Config :{code} Kode {error}"
                       .format(code=route["kode"], error=str(e)))
    # _logging.debug(f"Route: {route.get('kode')} {route.get('path')}")


def _add_route(config, route):
    if titles.get(route.get("kode")):
        _logging.warning(f"Route {route.get('kode')} sudah ada di titles")
        return

    if int(route.get("typ", 0)) in [0, 2]:
        config.add_route(route.get("kode"), route.get("path"))

    elif int(route.get("typ")) == 1:
        config.add_jsonrpc_endpoint(route.get("kode"), route.get("path"),
                                    default_renderer="json_rpc")
    if route.get("nama"):
        titles[route.get("kode")] = route.get("nama")



class AppClass:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.menus = []
        self.temp_files = ""
        self.captcha_files = ""
        self.partner_doc = ""
        self.login_tpl = ""
        self.allow_register = False

    def add_menu(self, config, route_menus, parent=None, paket="tsa_pos.views"):
        route_names = []
        for route in route_menus:
            # if not int(route.get("status", 0)):
            # continue

            route["route_name"] = [route["kode"]]
            route["permission"] = route.get("permission", "")
            route["icon"] = route.get("icon", None)
            route_typ = route.get("typ", 0) or route.get("type", 0) or 0
            if route_typ == "" or route_typ == None:
                route_typ = 0
            else:
                route_typ = int(route_typ)

            route["typ"] = route_typ
            is_menu = route.get("is_menu", 0)
            route["is_menu"] = is_menu and int(is_menu) or 0

            url_path = route.get("path", None)
            if not url_path:
                path_split = route.get("kode").split("-")
                path_last = path_split[len(path_split) - 1]
                if path_last in ["edit", "view", "delete"]:
                    path = "/".join(path_split[:-1])
                    path += "/{id}/"+path_last
                elif path_last in ["act"]:
                    path = "/".join(path_split[:-1])
                    path += "/{act}/"+path_last
                else:
                    path = "/".join(path_split)
                url_path = '/'+path

            route["path"] = url_path

            children = route.get("children", [])
            route["children"] = []
            if route.get("file_name"):
                _add_view_config(config, paket, route)
            elif route["path"] != "#":
                _add_route(config, route)

            if route.get("is_menu", None):
                if not parent:
                    self.menus.append(route)
                else:
                    parent["children"].append(route)
            if children:
                route["route_name"].extend(
                    self.add_menu(config, children, route, paket)
                )
            route_names.append(route["kode"])
        return route_names

    def route_from_csv_(self, config, paket="tsa_pos.views", rows=[]):
        new_routes = []
        for row in rows:
            status = row.get("status", 0) or 0
            if not row["kode"] or not int(status):
                continue

            status = int(status)
            row["children"] = []
            parent_id = row.get("parent_id") or row.get(
                "parent_id/routes.kode")
            if parent_id:
                self.route_children(new_routes, row)
            else:
                new_routes.append(row)

        self.add_menu(config, new_routes, None, paket)
      
    def route_from_csv(self, config, paket="tsa_pos.views", filename="routes.csv"):
        fullpath = os.path.join(self.base_dir, 'scripts', 'data', filename)
        if get_ext(filename) == ".csv":
            with open(fullpath) as f:
                rows = csv.DictReader(f, skipinitialspace=True)
                self.route_from_csv_(config, paket, rows=rows)

        else:
            import xlsx_dict_reader
            from openpyxl import load_workbook
            wb = load_workbook(fullpath, data_only=True)
            ws = wb.active
            rows = xlsx_dict_reader.DictReader(ws)  # skip_blank=True
            self.route_from_csv_(config, paket, rows=rows)

    
    def static_view(self, config, settings={}):
        static_url = settings.get('static_url', '/static')
        static_path = settings.get('static_path', 'tsa_pos:static')
        config.add_static_view(static_url, static_path, cache_max_age=3600)

    def read_config(self, settings):
        settings = settings or {}
        self.temp_files = settings.get("temp_files", tempfile.gettempdir())
        self.login_tpl = settings.get("login_tpl", "")
        self.captcha_files = settings.get("captcha_files", os.path.join(
            self.temp_files, "captcha") + os.sep)
        self.partner_doc = settings.get("partner_doc", os.path.join(
            self.temp_files, "partner") + os.sep)
        self.allow_register = settings.get("allow_register", False)
        

    def get_menus(self):
        _logging.debug(f"Menus: {self.menus}")
        return self.menus
    
BASE_APP = AppClass()

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # default_resource_registry.registry['jquery.maskMoney'] = {
    #     None: {"js": "opensipkd.base:static/jquery/jquery.maskMoney.min.js"}}
    if not settings.get('localization', ''):
        settings['localization'] = 'id_ID.UTF-8'

    locale.setlocale(locale.LC_ALL, settings['localization'])
    if 'timezone' not in settings:
        settings['timezone'] = 'Asia/Jakarta'
    # settings["captcha_files"] = "c:\\tmp\\captcha\\"
    tmp = settings.get("temp_files", tempfile.gettempdir())
    settings["temp_files"] = tmp
    settings['captcha_files'] = os.path.join(tmp, "captcha") + os.sep

    init_db(settings=settings)
    config = set_config(settings=settings)
    routes_file = settings.get("route_files") or "routes.csv"
    BASE_APP.route_from_csv(config=config, filename=routes_file)
    BASE_APP.static_view(config=config, settings=settings)
    BASE_APP.read_config(settings=settings)
    config.scan()
    return config.make_wsgi_app()


def has_permission_(request, perm_names, context=None):
    if not perm_names:
        return True
    if isinstance(perm_names, str):
        perm_names = [perm_names]
    for perm_name in perm_names:
        if request.has_permission(perm_name, context):
            return True
        
@subscriber(BeforeRender)
def add_global(event):
    event['has_permission'] = has_permission_
    event['get_base_menus'] = BASE_APP.get_menus
