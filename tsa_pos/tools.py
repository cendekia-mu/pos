import datetime
import os
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