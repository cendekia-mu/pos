from iso8601.iso8601 import ISO8601_REGEX
from deform.widget import string_types
import json
import logging

from colander import SchemaNode, null, Mapping, Invalid  # , string_types
# from colander import compat # tidak ada di colander 2.0
from deform import widget
from deform.compat import sequence_types, text_type, text_
from deform.form import Button
from deform.i18n import _
# from tangsel.tools.captcha import img_captcha
from datetime import date, datetime
_logging = logging.getLogger(__name__)


class Select2Widget(widget.Select2Widget):
    """
    Renders ``<select>`` field based on a predefined set of values using
    `select2 <https://select2.org/>`_ library.

    **Attributes/Arguments**

    Same as :func:`~deform.widget.Select2Widget`, with some extra options
    listed here.
    url: url for slave select
    slave: id of slave  select
    widget = widget_os.Select2MsWidget(url="https://slave_item_url?item_key=selected_value,
                                        slave="slave_id")
    """

    url = ""
    slave = ""
    template = "tsa_pos.widgets:select2_ms.pt"


class AutocompleteInputWidget(widget.AutocompleteInputWidget):
    """
    Renders ``<select>`` field based on a predefined set of values using
    `select2 <https://select2.org/>`_ library.

    **Attributes/Arguments**

    Same as :func:`~deform.widget.Select2Widget`, with some extra options
    listed here.
    url: url for slave select
    slave: id of slave  select
    widget = widget_os.AutocompleteMsInputWidget(url="https://slave_item_url?item_key=selected_value,
                                        slave="slave_id")

    Saat ini untuk slave baru bisa ke select2ms atau select2 atau select

    """

    url = ""
    slave = ""
    template = "tsa_pos.widgets:autocomplete_input_ms.pt"
    readonly_template = "tsa_pos.widgets:readonly/autocomplete_input_ms.pt"
    parent_oid = ""


    _pstruct_schema = SchemaNode(
        Mapping(),
        SchemaNode(widget._StrippedString(), name="auto_id"),
        SchemaNode(widget._StrippedString(), name="auto_value"),
    )

    def serialize(self, field, cstruct, **kw):
        if "delay" in kw or getattr(self, "delay", None):
            raise ValueError(
                "AutocompleteWidget does not support *delay* parameter "
                "any longer."
            )

        if cstruct is null:
            auto_id = ""
            auto_value = ""
        else:
            auto_id, auto_value = cstruct.split("|", 2)

        kw.setdefault("auto_id", auto_id)
        kw.setdefault("auto_value", auto_value)
        self.values = self.values or []
        readonly = kw.get("readonly", self.readonly)

        options = {}
        if isinstance(self.values, string_types):
            options["remote"] = "%s?term=%%QUERY" % self.values
        else:
            # vals = []
            # for v in self.values:
            #     if not isinstance(v, string_types):
            #         vals.append(v[1])
            # if not vals:
            # vals = self.values

            options["local"] = self.values

        options["minLength"] = kw.pop("min_length", self.min_length)
        options["limit"] = kw.pop("items", self.items)
        kw["options"] = json.dumps(options)
        kw["data"] = self.values

        template = readonly and self.readonly_template or self.template
        tmpl_values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **tmpl_values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        else:
            try:
                validated = self._pstruct_schema.deserialize(pstruct)
            except Invalid as exc:
                raise Invalid(field.schema, text_("Invalid pstruct: %s" % exc))
            auto_id = validated["auto_id"]
            auto_value = validated["auto_value"]

            if not auto_id and not auto_value:
                return null

            result = "|".join([auto_id, auto_value])
            if not auto_id or not auto_value:
                raise Invalid(field.schema, _("Incomplete Data"), result)

            return result


# class AutocompleteMdInputWidget(AutocompleteInputWidget):
#     """
#     Renders ``<select>`` field based on a predefined set of values using
#     `select2 <https://select2.org/>`_ library.

#     **Attributes/Arguments**

#     Same as :func:`~deform.widget.Select2Widget`, with some extra options
#     listed here.
#     url: url for slave select
#     slave: id of slave  select
#     widget = widget_os.AutocompleteMsInputWidget(url="https://slave_item_url?item_key=selected_value,
#                                         slave="slave_id")

#     Saat ini untuk slave baru bisa ke select2ms atau select2 atau select

#     """

#     url = ""
#     slave = ""
#     template = "autocomplete_input_md.pt"
#     readonly_template = "readonly/autocomplete_input_md.pt"

#     _pstruct_schema = SchemaNode(
#         Mapping(),
#         SchemaNode(_StrippedString(), name="auto_id"),
#         SchemaNode(_StrippedString(), name="auto_value"),
#     )

#     def serialize(self, field, cstruct, **kw):
#         if "delay" in kw or getattr(self, "delay", None):
#             raise ValueError(
#                 "AutocompleteWidget does not support *delay* parameter "
#                 "any longer."
#             )

#         if cstruct is null:
#             auto_id = ""
#             auto_value = ""
#         else:
#             auto_id, auto_value = cstruct.split("|", 2)

#         kw.setdefault("auto_id", auto_id)
#         kw.setdefault("auto_value", auto_value)
#         self.values = self.values or []
#         readonly = kw.get("readonly", self.readonly)

#         options = {}
#         if isinstance(self.values, string_types):
#             options["remote"] = "%s?term=%%QUERY" % self.values
#         else:
#             # vals = []
#             # for v in self.values:
#             #     if not isinstance(v, string_types):
#             #         vals.append(v[1])
#             # if not vals:
#             # vals = self.values

#             options["local"] = self.values

#         options["minLength"] = kw.pop("min_length", self.min_length)
#         options["limit"] = kw.pop("items", self.items)
#         kw["options"] = json.dumps(options)
#         kw["data"] = self.values

#         template = readonly and self.readonly_template or self.template
#         tmpl_values = self.get_template_values(field, cstruct, kw)
#         return field.renderer(template, **tmpl_values)

#     def deserialize(self, field, pstruct):
#         if pstruct is null:
#             return null
#         else:
#             try:
#                 validated = self._pstruct_schema.deserialize(pstruct)
#             except Invalid as exc:
#                 raise Invalid(field.schema, text_("Invalid pstruct: %s" % exc))
#             auto_id = validated["auto_id"]
#             auto_value = validated["auto_value"]

#             if not auto_id and not auto_value:
#                 return null

#             result = "|".join([auto_id, auto_value])
#             if not auto_id or not auto_value:
#                 raise Invalid(field.schema, _("Incomplete Data"), result)

#             return result

class QtyWidget(widget.Widget):
    template = "tsa_pos.widgets:qty.pt"
    readonly_template = "tsa_pos.widgets:readonly/qty.pt"

    _pstruct_schema = SchemaNode(
        Mapping(),
        SchemaNode(widget._StrippedString(), name="qty"),
        SchemaNode(widget._StrippedString(), name="measure"),
    )

    def serialize(self, field, cstruct, **kw):
        if cstruct is null:
            qty = 0
            measure = 0
        else:
            qty, measure = cstruct.split("|", 3)

        kw.setdefault("qty", qty)
        kw.setdefault("measure", measure)
        readonly = kw.get("readonly", self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        else:
            try:
                validated = self._pstruct_schema.deserialize(pstruct)
            except Invalid as exc:
                raise Invalid(field.schema, f"Invalid pstruct: {exc}")
            qty = validated["qty"]
            measure = validated["measure"]

            if not qty and not measure:
                return null

            result = "|".join([str(qty), str(measure)])

            if not qty or not measure:
                raise Invalid(field.schema, "Data tidak lengkap", result)

            return result


# class CaptchaWidget(widget.Widget):
#     """
#     Renders an ``<input type="text"/>`` widget.

#     **Attributes/Arguments**

#     template
#        The template name used to render the widget.  Default:
#         ``textinput``.

#     readonly_template
#         The template name used to render the widget in read-only mode.
#         Default: ``readonly/textinput``.

#     strip
#         If true, during deserialization, strip the value of leading
#         and trailing whitespace (default ``True``).

#     """

#     template = "tangsel.base:widgets/templates/captcha.pt"
#     readonly_template = "textinput"
#     strip = True
#     requirements = ()
#     request = None
#     url = ""
    
#     def __init__(self, **kw):
#         super(CaptchaWidget, self).__init__(**kw)

#     def serialize(self, field, cstruct, **kw):
#         kode_captcha, file_name = img_captcha(self.request)
#         self.request.session["captcha"] = kode_captcha
#         cstruct = self.url+file_name
#         readonly = kw.get("readonly", self.readonly)
#         template = readonly and self.readonly_template or self.template
#         values = self.get_template_values(field, cstruct, kw)
#         return field.renderer(template, **values)

#     def deserialize(self, field, pstruct):
#         if pstruct is null:
#             return null
#         elif not isinstance(pstruct, string_types):
#             raise Invalid(field.schema, "Pstruct is not a string")
#         if self.strip:
#             pstruct = pstruct.strip()
#         if not pstruct:
#             return null
#         if pstruct != self.request.session.get("captcha"):
#             raise Invalid(field.schema, "Captcha tidak sesuai")
#         return pstruct


class ImageWidget(widget.Widget):
    """
    Renders an ``<img src="src"/>`` widget.

    **Attributes/Arguments**

    template
       The template name used to render the widget.  Default:
        ``image``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/image``.

    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace (default ``True``).

    """

    template = "tsa_pos.widgets:image.pt"
    readonly_template = "tsa_pos.widgets:readonly/image.pt"
    strip = True
    requirements = ()
    height = "30px"

    def __init__(self, **kw):
        super().__init__(**kw)

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ""
        readonly = kw.get("readonly", self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        elif not isinstance(pstruct, string_types):
            raise Invalid(field.schema, "Pstruct is not a string")
        if self.strip:
            pstruct = pstruct.strip()
        if not pstruct:
            return null
        return pstruct


class BootStrapDateInputWidget(widget.Widget):
    """
    Renders a date picker widget.

    The default rendering is as a native HTML5 date input widget,
    falling back to pickadate (https://github.com/amsul/pickadate.js.)

    Most useful when the schema node is a ``colander.Date`` object.

    **Attributes/Arguments**

    options
        Dictionary of options for configuring the widget (eg: date format)

    template
        The template name used to render the widget.  Default:
        ``dateinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textinput``.
    """
    template = "tsa_pos.widgets:bootstrapdateinput"
    readonly_template = "textinput"
    type_name = "text"
    req_path = "tsa_pos:static/js/plugin"
    requirements = (
        ('deform', None),
        {
            "js": (
                f"{req_path}/bootstrap-datepicker/js/bootstrap-datepicker.min.js",
                f"{req_path}/bootstrap-timepicker/bootstrap-timepicker.min.js",
                f"{req_path}/bootstrap-datetimepicker/js/bootstrap-datetimepicker.min.js",
            ),
            "css": (
                f"{req_path}/bootstrap-datepicker/css/bootstrap-datepicker.min.css",
                # f"{req_path}/bootstrap-timepicker/css/bootstrap-timepicker.min.css",
                f"{req_path}/bootstrap-datetimepicker/css/bootstrap-datetimepicker.min.css",
            ),
        }
    )
    default_options = (
        ("format", "yyyy-mm-dd"),
        ("zIndexOffset", "910"),

    )
    # ("selectMonths", True),
    # ("selectYears", True),
    options = None

    _pstruct_schema = SchemaNode(
        Mapping(),
        SchemaNode(widget._StrippedString(), name="date"),
        SchemaNode(widget._StrippedString(), name="date_submit", missing=""),
    )

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ""
        else:
            cstruct = cstruct.split(" ")[0]
        readonly = kw.get("readonly", self.readonly)
        template = readonly and self.readonly_template or self.template
        options = dict(
            kw.get("options") or self.options or self.default_options
        )
        options["formatSubmit"] = "yyyy-mm-dd"
        kw.setdefault("options_json", json.dumps(options))
        cstruct = cstruct and type(cstruct)==datetime and date(cstruct) or cstruct
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct in ("", null):
            return null
        try:
            validated = self._pstruct_schema.deserialize(pstruct)
        except Invalid as exc:
            raise Invalid(field.schema, "Invalid pstruct: %s" % exc)
        return validated["date_submit"] or validated["date"]


class BootStrapDateTimeInputWidget(widget.Widget):
    """
    Renders a datetime picker widget.

    The default rendering is as a pair of inputs (a date and a time) using
    pickadate.js (https://github.com/amsul/pickadate.js).

    Used for ``colander.DateTime`` schema nodes.

    **Attributes/Arguments**

    date_options
        A dictionary of date options passed to pickadate.

    time_options
        A dictionary of time options passed to pickadate.

    template
        The template name used to render the widget.  Default:
        ``dateinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textinput``.
    """

    template = "tsa_pos.widgets:datetimeinput"
    readonly_template = "tsa_pos.widgets:readonly/datetimeinput"
    type_name = "datetime"
    requirements = (("modernizr", None), ("pickadate", None))
    default_date_options = (
        ("format", "yyyy-mm-dd"),
        ("selectMonths", True),
        ("selectYears", True),
    )
    date_options = None
    default_time_options = (("format", "h:i A"), ("interval", 30))
    time_options = None

    _pstruct_schema = SchemaNode(
        Mapping(),
        SchemaNode(widget._StrippedString(), name="date"),
        SchemaNode(widget._StrippedString(), name="time"),
        SchemaNode(widget._StrippedString(), name="date_submit", missing=""),
        SchemaNode(widget._StrippedString(), name="time_submit", missing=""),
    )

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ""
        readonly = kw.get("readonly", self.readonly)
        if cstruct:
            parsed = ISO8601_REGEX.match(cstruct)
            if parsed:  # strip timezone if it's there
                timezone = parsed.groupdict()["timezone"]
                if timezone and cstruct.endswith(timezone):
                    cstruct = cstruct[: -len(timezone)]

        try:
            date, time = cstruct.split("T", 1)
            try:
                # get rid of milliseconds
                time, _ = time.split(".", 1)
            except ValueError:
                pass
            kw["date"], kw["time"] = date, time
        except ValueError:  # need more than one item to unpack
            kw["date"] = kw["time"] = ""

        date_options = dict(
            kw.get("date_options")
            or self.date_options
            or self.default_date_options
        )
        date_options["formatSubmit"] = "yyyy-mm-dd"
        kw["date_options_json"] = json.dumps(date_options)

        time_options = dict(
            kw.get("time_options")
            or self.time_options
            or self.default_time_options
        )
        time_options["formatSubmit"] = "HH:i"
        kw["time_options_json"] = json.dumps(time_options)

        values = self.get_template_values(field, cstruct, kw)
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        else:
            try:
                validated = self._pstruct_schema.deserialize(pstruct)
            except Invalid as exc:
                raise Invalid(field.schema, "Invalid pstruct: %s" % exc)
            # seriously pickadate?  oh.  right.  i forgot.  you're javascript.
            date = validated["date_submit"] or validated["date"]
            time = validated["time_submit"] or validated["time"]

            if not time and not date:
                return null

            result = "T".join([date, time])

            if not date:
                raise Invalid(field.schema, _("Incomplete date"), result)

            if not time:
                raise Invalid(field.schema, _("Incomplete time"), result)

            return result


class TextInputBtnWidget(widget.TextInputWidget):
    template = "tsa_pos.widgets:textinput_btn"
    button = None
    js = None

    def __init__(self, **kw):
        super().__init__(**kw)

        # if isinstance(self.button, compat.string_types):
        if self.button:
            if isinstance(self.button, str):
                self.button = Button(self.button, type="button")


class DateInputWidget(widget.DateInputWidget):
    type_name = "text"


class MoneyInputWidget(widget.MoneyInputWidget):
    """
    Renders an ``<input type="text"/>`` widget with Javascript which enforces
    a valid currency input.  It should be used along with the
    ``colander.Decimal`` schema type (at least if you care about your money).
    This widget depends on the ``jquery-maskMoney`` JQuery plugin.

    **Attributes/Arguments**

    template
       The template name used to render the widget.  Default:
        ``moneyinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textinput``.

    options
        A dictionary or sequence of two-tuples containing ``jquery-maskMoney``
        options.  The valid options are:

        symbol
            the symbol to be used before of the user values. default: ``$``

        showSymbol
            set if the symbol must be displayed or not. default: ``False``

        symbolStay
            set if the symbol will stay in the field after the user exists the
            field. default: ``False``

        thousands
            the thousands separator. default: ``,``

        decimal
            the decimal separator. default: ``.``

        precision
            how many decimal places are allowed. default: 2

        defaultZero
            when the user enters the field, it sets a default mask using zero.
            default: ``True``

        allowZero
            use this setting to prevent users from inputing zero. default:
            ``False``

        allowNegative
            use this setting to prevent users from inputing negative values.
            default: ``False``
    """
    readonly_template = "readonly/textinput"

    def get_template_values(self, field, cstruct, kw):
        options = json.loads(kw.get("mask_options", "{}"))
        if options:
            decimal = options.get("decimal", '.')
            precision = options.get("precision", 2)
            thousands = options.get("thousands", ',')
            cstr = cstruct and float(cstruct) or 0
            cstruct = f"{cstr:,.{precision}f}"\
                .replace(".", "%")\
                .replace(",", thousands)\
                .replace("%", decimal)
        
        else:
            precision = 0
            cstr = cstruct and float(cstruct) or 0
            cstruct = f"{cstr:,.{precision}f}"
            
        values = {"cstruct": cstruct, "field": field}
        values.update(kw)
        values.pop("template", None)
        return values


class FilterWidget(widget.Widget):
    template = "tsa_pos.widgets:filters.pt"
    readonly_template = "tsa_pos.widgets:readonly/filters.pt"
    null_value = ""
    values = ()
    size = None
    multiple = False
    optgroup_class = widget.OptGroup
    long_label_generator = None
    selectize_options = None
    default_selectize_options = (("allowEmptyOption", True),)

    _pstruct_schema = SchemaNode(
        Mapping(),
        SchemaNode(widget._StrippedString(), name="fields"),
        SchemaNode(widget._StrippedString(), name="equality"),
        SchemaNode(widget._StrippedString(), name="nilai"),
        SchemaNode(widget._StrippedString(), name="condition"),
    )

    def get_select_value(self, cstruct, value):
        """Choose whether <opt> is selected or not.

        Incoming value is always string, as it has been passed through HTML.
        However, our values might be given as integer, UUID.
        """

        if self.multiple:
            if value in map(text_type, cstruct):
                return "selected"
        else:
            if value == text_type(cstruct):
                return "selected"
        return None

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            condition = ""
            fields = ""
            equality = ""
            nilai = ""
        else:
            fields, equality, nilai, condition = cstruct.split(".", 4)
        # if cstruct in (null, None):
        #     cstruct = self.null_value
        kw.setdefault("condition", condition)
        kw.setdefault("fields", fields)
        kw.setdefault("equality", equality)
        kw.setdefault("nilai", nilai)

        readonly = kw.get("readonly", self.readonly)
        values = kw.get("values", self.values)
        if not isinstance(values, sequence_types):
            e = "Values must be a sequence type (list, tuple, or range)."
            raise TypeError(e)

        template = readonly and self.readonly_template or self.template
        kw["values"] = widget._normalize_choices(values)
        selectize_options = dict(
            kw.get("selectize_options")
            or self.selectize_options
            or self.default_selectize_options
        )
        kw["selectize_options_json"] = json.dumps(selectize_options)
        tmpl_values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **tmpl_values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        else:
            try:
                validated = self._pstruct_schema.deserialize(pstruct)
            except Invalid as exc:
                raise Invalid(field.schema, f"Invalid pstruct: {exc}")
            condition = validated["condition"]
            fields = validated["fields"]
            equality = validated["equality"]
            nilai = validated["nilai"]

            # if not year and not bundle and not seq:
            #     return null
            #
            # if self.assume_y2k and len(year) == 2:
            #     year = "20" + year
            result = ".".join([fields, equality, nilai, condition])
            #
            # if not year or not bundle or not seq:
            #     raise Invalid(field.schema, "No Dokumen tidak lengkap", result)

            return result

