from calendar import c
from datetime import datetime, timedelta
import os
from urllib import request

from deform import form, widget
from ..tools import get_settings, sending_mail, two_minutes
import colander
import logging
import deform
from pyramid.httpexceptions import HTTPFound
from .base_view import BaseViews, CSRFSchema
from tsa_pos import BASE_APP, scripts
from ziggurat_foundations.models.services.user import UserService
from pyramid.security import remember, forget
from pyramid.response import Response
from pyramid.renderers import render_to_response
# from tsa_pos.tools import xhr_response
from ..models import DBSession, User
from ..tools import create_now, set_user_log, get_settings
from ..i18n import _
from deform import Form, Button

_logging = logging.getLogger(__name__)


class LoginSchema(CSRFSchema):
    username = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(
        colander.String(), widget=deform.widget.PasswordWidget())


class LogoutSchema(CSRFSchema):
    message = colander.SchemaNode(
        colander.String(),
        missing=colander.drop,
        widget=widget.TextInputWidget(readonly=True),
        title=_("You have been logged out successfully.")
        )


def get_login_headers(request, user):
    UserService.regenerate_security_code(user)
    headers = remember(request, user.id)
    headers.append(("Token", user.security_code))
    _logging.debug(headers)
    user.last_login_date = create_now()
    DBSession.add(user)
    DBSession.flush()
    return headers


def xhr_response(user, headers):
    # partner = Partner.query_email(user.email).first()
    partner = None
    mobile = partner and partner.mobile or ""
    nama = partner and partner.nama or ""
    data = {
        "data":
            [{
                "user_id": user.user_name,
                "permission": user.get_permissions(),
                "token": user.security_code,
                "mobile": mobile,
                "email": user.email,
                "nama": nama,
            }]
    }
    return Response(json=data, headerlist=headers)


class LoginUser(object):
    def __init__(self, request):
        # self.user = user
        self.request = request
        # self.identity=identity
        self.message = "Sukses Login"
        self.user = None

    def login(self, values, user=None):
        self.user = user and user or User.get_by_identity(values["username"])
        if not self.user or not UserService.check_password(
                self.user, values["password"]):
            self.message = "Login Gagal"
            set_user_log(self.message, self.request,
                         _logging, values["username"])
            return
        for g in self.user.groups:
            _logging.debug(f"Group: {g.id} as {g.group_name}")

        # generate security_code dan simpan dalam session
        regenerate_security_code(self.user, 0.03)  # berlaku selama 1.8 menit
        # dicek pada module security get_user
        self.request.session["token"] = self.user.security_code
        return True


def regenerate_security_code(user, hour=1.0):
    hour = timedelta(float(hour) / 24.0)
    age = security_code_age(user)
    remain = hour - age
    if user.security_code and age < hour and remain > two_minutes:
        _logging.debug("Security code: %s", user.security_code)
        return remain
    UserService.regenerate_security_code(user)
    user.security_code_date = create_now()
    _logging.debug("Security code: %s", user.security_code)
    DBSession.add(user)
    return hour


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)

    def form_validator(self, form, values):
        exc = colander.Invalid(form, 'Login gagal')
        identity = values.get('username')
        user = User.get_by_identity(identity)  # form.schema.user =
        login = LoginUser(self.request)
        if not login.login(values, user):
            self.request.session.flash(login.message, "error")
            exc["username"] = login.message
            exc["password"] = login.message
            msg = 'Login gagal'
            set_user_log(msg, self.request, _logging, identity)
            raise exc
        values['user'] = user

    def login(self):
        request = self.request
        login_tpl = BASE_APP.login_tpl
        home = request.route_url('home')
        if request.authenticated_userid:  # (request):
            message = 'Anda sudah login'
            if request.is_xhr:
                user = request.user
                headers = get_login_headers(request, user)
                return xhr_response(user, headers)
            request.session.flash(message, 'error')
            return HTTPFound(location=f"{home}")

        # request.session["login"] = True
        next_url = request.params.get('next', request.referrer)
        if not next_url:
            next_url = home

        buttons = (Button('login', _('Login')),)
        if BASE_APP.allow_register:
            buttons += (Button('register', _('Register')),)
        buttons += (Button('reset', _('Reset')),
                    Button('cancel', _('Cancel')),)
        form = self.get_form(LoginSchema, buttons=buttons)

        if request.POST:
            if 'cancel' in request.POST:
                return HTTPFound(location=home)
            elif 'register' in request.POST:
                return HTTPFound(location=request.route_url('register'))
            elif 'login' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except deform.ValidationFailure as e:
                    if self.req.is_xhr:
                        d = {"error": e.error.asdict()}
                        return Response(json=d)
                    return HTTPFound(location=request.route_url('login'))
                return redirect_login(request, c["user"])

        if login_tpl:
            return render_to_response(
                renderer_name=login_tpl,
                request=request,
                value=dict(form=form,
                           message=message,
                           url=request.route_url('login'),
                           next_url=next_url,
                           login=LoginUser(request), ),
            )
        rendered_form = form.render()
        return {'form': rendered_form, "scripts": ""}

    def logout(self):
        request = self.request
        if self.request.authenticated_userid is None:
            form = self.get_form(LogoutSchema, buttons=('home', 'login'))
            if request.POST:
                if 'home' in request.POST:
                    return HTTPFound(location=request.route_url('home'))
                elif 'login' in request.POST:   
                    return HTTPFound(location=request.route_url('login'))
            return {"form": form.render(), "scripts": ""}

        headers = forget(request)
        request.session.delete()
        request.response.headers.update(headers)
        set_user_log("Logout", self.request, _logging)
        return HTTPFound(location=request.route_url('logout'),headers=headers)
        

def security_code_age(user):
    now = create_now()
    if user.security_code_date:
        return now - user.security_code_date
    return timedelta(minutes=1)


def redirect_login(request, user):
    set_user_log("Login Sukses", request, _logging, user.user_name)
    for g in user.groups:
        _logging.debug(f"Group: {g.id} as {g.group_name}")

    headers = get_login_headers(request, user)
    if request.is_xhr:
        return xhr_response(user, headers)
    next_url = request.params.get('next')

    if not next_url and request.matched_route.name == 'login':
        url = get_settings().get('modules_default', 'home')
        return HTTPFound(location=request.route_url(url),
                         headers=headers)
    if not next_url:
        next_url = request.route_url('home')

    return HTTPFound(location=next_url, headers=headers)


def send_email_security_code(
        request, user, time_remain, subject, body_msg_id, body_default_file,
        **kwargs):
    settings = get_settings()
    password = kwargs.get("password", "")
    if 'mail.sender_name' not in settings or 'mail.username' not in settings:
        return

    url = '{}/password/{}/request'.format(
        request.home, user.security_code, password)

    minutes = int(time_remain.seconds / 60)
    data = dict(url=url, minutes=minutes)
    here = os.path.abspath(os.path.dirname(__file__))
    body_file = os.path.join(here, body_default_file)
    with open(body_file) as f:
        body_tpl = f.read()

    body = _(body_msg_id, default=body_tpl, mapping=data)
    # body = request.localizer.translate(body)
    # sender = '{} <{}>'.format(
    #     settings['mail.sender_name'], settings['mail.username'])
    # subject = request.localizer.translate(_(subject))
    # message = Message(
    #     subject=subject, sender=sender, recipients=[user.email], body=body)
    # mailer = request.registry['mailer']
    # mailer.send(message)
    sending_mail(request, user, subject, body)
