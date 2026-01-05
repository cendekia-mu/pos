"""Form."""
# Standard Library
import json
import logging
import re

import colander
from deform import compat, widget as deform_widget, field

from . import widget

log = logging.getLogger(__name__)


class DeTable(field.Field):
    css_class = "deform" 

    def __init__(
            self,
            schema,
            action,
            action_suffix='/grid/act',
            buttons=(),
            tableid="detable",
            sorts='true',
            filters='true',
            paginates='true',
            params="",
            server_side=True,
            state_save=True,
            data=[],
            allow_edit=True,
            allow_delete=True,
            allow_view=True,
            allow_post=False,
            allow_unpost=False,
            allow_check=False,
            check_field=False,
            filter_columns=False,
            scroll_x=False,
            scroll_y=False,
            **kw
    ):
        kw.pop("parent", None)  
        super().__init__(schema, **kw)
        self.request = kw.get("request")
        self.rows = kw.get("rows")
        
        # --- FIX: URL Sanitization untuk mencegah triple slash ---
        clean_action = action.rstrip('/')
        clean_suffix = '/' + action_suffix.lstrip('/')
        
        self.action = clean_action
        self.tableid = tableid
        self.data = data
        self.allow_edit = json.dumps(allow_edit)
        self.allow_delete = json.dumps(allow_delete)
        self.allow_view = json.dumps(allow_view)
        self.allow_post = json.dumps(allow_post)
        self.allow_unpost = json.dumps(allow_unpost)
        self.allow_check = json.dumps(allow_check)
        self.check_field = json.dumps(check_field)
        self.filter_columns = filter_columns # Disimpan sebagai data, bukan method
        self.scroll_x = json.dumps(scroll_x)
        self.scroll_y = json.dumps(scroll_y)

        html_buttons = kw.get("html_buttons", None)
        new_buttons = kw.get("new_buttons") or {}
        
        params_str = params and f"?{params}" or ""
        self.url_suffix = f"{clean_suffix}{params_str}"

        # Perbaikan logika close_url
        close_url = self.action
        if close_url and "://" not in close_url[:10]:
            parts = close_url.split("/")
            close_url = "/".join(parts[:-1]) if len(parts) > 1 else "/"
        
        dict_buttons = {
            "close": "{window.location = '" + close_url + "'; return false;}",
            "add": "{window.location = o%sUri+'/add%s';}" % (tableid, params_str),
            "edit": """{
                if (m%sID) window.location = o%sUri+'/'+m%sID+'/edit%s';
                else alert('Pilih Baris');
                }""" % (tableid, tableid, tableid, params_str),
            "view": "{window.location = o%sUri+'/'+m%sID+'/view%s';}" % (
                tableid, tableid, params_str),
            "delete": "{window.location = o%sUri+'/'+m%sID+'/delete%s';}" % (
                tableid, tableid, params_str),
            "csv": "{window.location = o%sUri+'/csv/act%s';}" % (
                tableid, params_str),
            "pdf": "{window.open(o%sUri+'/pdf/act%s');}" % (tableid, params_str),
            "upload": "{window.location = o%sUri+'/upload%s';}" % (
                tableid, params_str),
        }

        for k in new_buttons:
            buttons += (new_buttons[k]["obj"],)
            dict_buttons[k] = '{' + new_buttons[k]["js"].format(tableid=tableid,
                                                                params=params_str) + '}'

        obj_buttons = []
        _scripts = []
        for button in buttons:
            if isinstance(button, compat.string_types):
                button = Button(button)
            obj_buttons.append(button)
        
        header_buttons = []
        for button in obj_buttons:
            header_buttons.append(
                f"""<button id="{tableid}{button.name}" name="{button.name}" type="{button.type}" class="btn {button.css_class}"> {button.title} </button>\n""")
            _scripts.append(f'$("#{tableid + button.name}").click(function ()' +
                            dict_buttons[button.name] + ');')

        if html_buttons:
            for html in html_buttons:
                header_buttons.append(html["obj"])
                _scripts.append(html["js"])

        if filter_columns:
            f_button = f"""<a href="#{tableid}-form-filter" data-toggle="collapse" class= "btn btn-warning dropdown">Filters</a>"""
            header_buttons.insert(0, f_button)

        edit_buttons = []
        if allow_check:
            c_button = f"""<input type="checkbox" class="{tableid}checkAll form-control"> All</input>"""
            edit_buttons.append(c_button)

        self.buttons = "','".join(header_buttons).replace('\n', "").replace(';', ';\n')
        self.edit_buttons = "','".join(edit_buttons).replace('\n', "").replace(';', ';\n')
        self.scripts = ''.join(_scripts).replace(';', ";\n")

        table_widget = getattr(schema, "widget", None)
        if table_widget is None:
            table_widget = widget.TableWidget()

        self.widget = table_widget
        self.server_side = json.dumps(server_side)
        self.data = data
        columns = []
        headers = []

        filter_form = ""
        field_index = 0
        for f in schema:
            field_index += 1
            d = {'data': f.name, 'title': f.title}
            
            for attr in ['width', 'aligned', 'searchable', 'visible', 'orderable']:
                if hasattr(f, attr):
                    val = getattr(f, attr)
                    if attr == 'aligned':
                        d["className"] = val
                    else:
                        d[attr] = val

            d["action"] = getattr(f, "action", True)
            
            if isinstance(f.widget, deform_widget.HiddenWidget):
                d["visible"] = False
            elif isinstance(f.widget, deform_widget.CheckboxWidget):
                d.update(self.widget_checkbox(f))
            elif isinstance(f.widget, deform_widget.SelectWidget):
                d.update(self.widget_select(f))
            else:
                d["wg_checkbox"] = False
                d["wg_select"] = False

            if hasattr(f, "url"):
                u = f.url
                d["render"] = f"function(data){{ let r = 'No Data'; if (data != null) r = '<a href=\"{u}' + data + '\" target=\"_blank\">Link</a>&nbsp;'; return r; }}"

            if f.name == "id" and self.action:
                d.setdefault("orderable", True)
                d["width"] = getattr(f, "width", "40pt")
                d["className"] = "text-center"
                d["visible"] = True
                d["render"] = f"function (id) {{ return {self.action_url(f)}; }}"

            if filter_columns and getattr(f, "searchable", False):
                filter_form += self.get_filter_form(f, field_index)

            thousand = getattr(f, 'thousand', None)
            if thousand or isinstance(f.typ, (colander.Float, colander.Integer)):
                sep = thousand.get("separator", ",") if thousand else ","
                dec = thousand.get("decimal", ".") if thousand else "."
                prec = thousand.get("precision", thousand.get("point", 0)) if thousand else 0
                curr = thousand.get("currency", "") if thousand else ""
                d["render"] = f"$.fn.dataTable.render.number('{sep}', '{dec}', {prec}, '{curr}')"
                d.setdefault("className", "text-right")

            columns.append(d)
            headers.append(f.title)

        # --- FIX: Tambahkan atribut agar template .pt tidak error ---
        self.filter_form = filter_form
        self.filter_scripts = "" # Mengisi attribute yang diminta detable.pt
        self.headers = headers
        self.head = headers
        self.columns = json.dumps(columns).replace('"$.fn.dataTable.render.number', "$.fn.dataTable.render.number").replace(')\"', ")")
        
        self.url = self.action
        self.url_suffix = self.url_suffix
        self.sorts = sorts
        self.paginates = paginates
        self.filters = filters
        self.state_save = json.dumps(state_save)

    def widget_checkbox(self, column):
        return {"wg_checkbox": True, "wg_checkbox_val": [column.widget.true_val, column.widget.false_val], "className": "text-center", "width": "30pt"}

    def widget_select(self, column):
        vals = column.widget.values
        d = {"wg_select": True, "wg_select_val": dict(vals) if isinstance(vals, list) else vals}
        return d

    def action_url(self, f):
        act = ""
        templates = {'allow_view': ('view', 'fa-eye', 'View'), 'allow_edit': ('edit', 'fa-edit', 'Edit'), 'allow_delete': ('delete', 'fa-trash', 'Delete')}
        for attr, (path, icon, title) in templates.items():
            if getattr(self, attr):
                act += f"'<a href=\"{self.action}/' + id + '/{path}\"><i class=\"fas {icon}\" aria-hidden=\"true\" title=\"{title}\"></i></a>' + "
        return act.rstrip(' + ')

    def get_filter_form(self, f, field_index):
        field_index -= 1
        col_id = f"{self.tableid}-{f.name}"
        html = f'<div class="form-group"><label>{f.title}</label>'
        if isinstance(f.widget, deform_widget.CheckboxWidget):
            html += f'<div class="input-group"><input type="radio" name="{col_id}" value="" data-index="{field_index}"> Semua </div>'
        else:
            html += f'<input type="text" class="form-control {self.tableid}-control-filter" placeholder="{f.title}" data-index="{field_index}">'
        return html + '</div>'

    def get_filter_scripts(self, f):
        return ""


class Button(object):
    def __init__(self, name="view", oid=None, title=None, type="button", css_class=None, icon=None, attributes=None, disabled=None):
        self.attributes = attributes or {}
        self.title = title or name.capitalize()
        self.name = re.sub(r"\s", "_", name)
        self.oid = oid or f"detable_btn_{self.name}"
        self.type = type
        self.disabled = disabled
        self.css_class = css_class or "btn-default"
        self.icon = icon