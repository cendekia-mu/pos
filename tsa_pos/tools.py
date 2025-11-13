import datetime
import os
import pytz
from pyramid.threadlocal import get_current_registry
import logging
from email.message import Message

_logging = logging.getLogger(__name__)

def get_settings():
    return get_current_registry().settings

def dmy(tgl):
    """
    Conversi dari date to string
    """
    if not tgl:
        return "00-00-0000"
    return tgl.strftime('%d-%m-%Y')

def dmyhms(tgl):
    return tgl.strftime('%d-%m-%Y %H:%M:%S')


def ymd(tgl):
    return tgl.strftime('%Y-%m-%d')


def ymdhms(tgl):
    return tgl.strftime('%Y-%m-%d %H:%M:%S')


def dMy(tgl):
    return tgl.strftime('%d %B %Y')


def format_datetime(v):
    if v.time() != datetime.time(0, 0):
        return dmyhms(v)
    else:
        return dmy(v)

def get_timezone():
    settings = get_settings()
    return pytz.timezone(settings['timezone'])


def create_now():
    tz = get_timezone()
    return datetime.datetime.now(tz)

class CSVRenderer:
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.writer(output)
        for row in value:
            writer.writerow(row)
        response = system['request'].response
        response.content_type = 'text/csv'
        response.content_disposition = 'attachment; filename="data.csv"'
        return output.getvalue()
    

def get_ext(filename):
    return os.path.splitext(filename)[1].lower()


def set_user_log(message, request, logobj=None, user_name=None):
    if not logobj:
        logobj =    _logging

    if not request:
        logobj.info("Request not Set")
        return

    if not user_name:
        user_name = request and request.user and request.user.user_name or None

    if not user_name:
        logobj.info("User Name not Set")
        return

    addr = request.client_addr
    message = "User {} at Addr {}: {}".format(user_name, addr, message)
    logobj.warning(message)


def sending_mail(request, user, subject, body):
    settings = get_settings()
    body = request.localizer.translate(body)
    sender = '{} <{}>'.format(
        settings['mail.sender_name'], settings['mail.username'])
    subject = request.localizer.translate(_(subject))
    message = Message(
        subject=subject, sender=sender, recipients=[user.email], body=body)
    mailer = request.registry['mailer']
    mailer.send(message)
from datetime import timedelta

one_hour = timedelta(1.0 / 24)
two_minutes = timedelta(1.0 / 24 / 60)


