import os
import sys
import ntpath
import csv
import io
import datetime 
# from z3c.rml import rml2pdf
import subprocess
import logging

# from pypdf import PdfReader, PdfWriter

from ..tools import get_settings, get_params, get_random_string

log = logging.getLogger(__name__)


# def get_root_path():
#     _here = os.path.dirname(__file__)
#     return _here


def get_logo(base_path=""):
    if not base_path:
        import opensipkd.base
        base_path = os.path.dirname(os.path.abspath(opensipkd.base.__file__))
    path = get_params('report_img', os.path.join(base_path, 'static/img'))
    return path + "/logo.png", path + "/line.png"


def waktu():
    return datetime.datetime.now().strftime('%d-%m-%Y %H:%M')


def open_rml_row(row_tpl_filename):
    f = open(row_tpl_filename)
    row_rml = f.read()
    f.close()
    return row_rml


def open_rml_pdf(tpl_filename, **kwargs):
    # out_filename = 'out_filename' in kwargs and kwargs['out_filename'] or tpl_filename
    # log.warning("Not Supported")
    # return
    pdf_filename = tpl_filename + '.pdf'
    f = open(tpl_filename)
    rml = f.read()
    f.close()
    base_path = kwargs.get('base_path')
    logo, line = get_logo(base_path)
    params = {}

    for key, value in kwargs.items():
        params[key] = value
    rml = rml.format(waktu=waktu(),
                     logo=logo,
                     line=line, **kwargs
                     )
    from z3c.rml import rml2pdf
    pdf = rml2pdf.parseString(rml)
    return pdf, pdf_filename


def openfile_response(request, filepath):
    response = request.response
    # import magic
    # ctype = magic.from_file(filepath, mime=True)
    f = open(filepath, 'rb')
    filename = ntpath.basename(filepath)
    import mimetypes
    ctype = mimetypes.MimeTypes().guess_type(filename)[0]
    response.content_type = str(ctype)
    response.content_disposition = 'filename=' + filename
    response.write(f.read())
    return response


def file_response(request, f=None, filename=None, filetype=None):
    """
    :param request:
    :param f:  object file
    :param filename:
    :param filetype: type of file
    :return: object response
    """
    import ntpath
    if not f:
        f = open(filename, 'rb')
        fname = ntpath.basename(filename)
    else:
        fname = filename

    if not filetype:
        t = fname.split('.')
        filetype = ''.join(t[-1:])

    response = request.response
    response.content_type = f"application/{filetype}"
    # dikarenakan dibrowser selalu muncul fullpath dari file yg ditampilkan, maka diganti
    # response.content_disposition = 'filename=' + fname
    response.content_disposition = 'filename=' + os.path.basename(fname)

    if filetype == "txt":
        response.charset = "UTF-8"
    response.write(f.read())
    return response


def set_response(request, filename):
    ext = filename.split('.')[-1]
    if ext in ['gif', 'png', 'jpeg', 'jpg']:
        ext = 'image/' + ext
    elif ext in ['pdf']:
        ext = 'application/' + ext
    with open(filename, 'rb') as f:
        return file_response(request, f, filename, ext)


def pdf_response(request, f=None, filename=None):
    return file_response(request, f, filename, 'pdf')


def odt_response(request, f, filename):
    return file_response(request, f, filename, 'odt')


def odt_export1(request, filename, file_type):
    settings = get_settings()
    if 'unoconv_py' in settings and settings['unoconv_py']:
        unoconv_py = settings['unoconv_py']
        if 'unoconv_bin' in settings and settings['unoconv_bin']:
            unoconv_bin = settings['unoconv_bin']
            f = '.'.join([filename, 'odt'])
            subprocess.call([unoconv_py, unoconv_bin, file_type, f])
            out_filename = '.'.join([filename, file_type])
            with open(out_filename, 'rb') as f:
                return file_response(request, f, out_filename, file_type)


def odt_export_(filename, file_type, password=None):
    log.info("Start Export {}".format(filename))
    settings = get_settings()
    import getpass
    username = getpass.getuser()
    odt_file = '.'.join([filename, 'odt'])
    out_dir = os.path.dirname(filename)
    if 'unoconv_py' in settings and settings['unoconv_py']:
        log.info("Unoconv PY {}".format(filename))
        unoconv_py = settings['unoconv_py']
        if 'unoconv_bin' in settings and settings['unoconv_bin']:
            unoconv_bin = settings['unoconv_bin']
        else:
            unoconv_bin = ''

        params = [unoconv_py, unoconv_bin, '-f', file_type]
        if password:
            params.extend(['-e', 'EncryptFile=True',
                           '-e', 'DocumentOpenPassword=' + password])

        params.append(odt_file)
        log.info("DEBUG EXPORT>>{}".format(' '.join(params)))
        subprocess.call(params)

    # convert using bin
    else:
        log.info("Unoconv BIN {}".format(filename))
        if 'unoconv_bin' in settings and settings['unoconv_bin']:
            unoconv_bin = settings['unoconv_bin']
            params = [unoconv_bin,
                      '-env:UserInstallation=file:///tmp/' + username,
                      '--headless', '--convert-to', 'pdf']
            params.extend(['--outdir', out_dir, file_type, odt_file])
            log.info("DEBUG EXPORT>>{}".format(' '.join(params)))
            subprocess.call(params)

    out_file = '.'.join([filename, file_type])
    if not os.path.isfile(odt_file):
        log.error("ODT FILE NOTFOUND")
        return dict(error=dict(code=-1,
                               message='File  %s tidak ditemukan ' % odt_file))
    else:
        if not os.path.isfile(out_file):
            log.error("PDF FILE NOTFOUND")
            return dict(error=dict(code=-1,
                                   message='File  %s tidak ditemukan ' % out_file))
        os.remove(odt_file)
    return dict(filename=out_file)


def odt_export(request, filename, file_type):
    results = odt_export_(filename, file_type)
    # bug key error: code
    # if not results['code']:
    if 'error' in results:
        return results

    # out_filename = '.'.join([filename, file_type])
    # out_filename = '.'.join([results['filename'], file_type])
    out_filename = results['filename']

    if not os.path.isfile(out_filename):
        return dict(error=True,
                    msg='Error %s tidak ditemukan ' % out_filename)

    with open(out_filename, 'rb') as f:
        return file_response(request, f, out_filename, file_type)


def odt_export2(request, filename, file_type):
    settings = get_settings()
    if 'unoconv_py' in settings and settings['unoconv_py']:
        if 'unoconv_bin' in settings and settings['unoconv_bin']:
            unoconv_py = settings['unoconv_py']
            unoconv_bin = settings['unoconv_bin']
            f = '.'.join([filename, 'odt'])
            subprocess.call([unoconv_bin,
                             '-env:UserInstallation=file:///tmp/libO_udir',
                             '--headless', '--convert-to', file_type,
                             '--outdir', '/tmp', f])
            out_filename = '.'.join([filename, file_type])
            with open(out_filename, 'rb') as f:
                return file_response(request, f, out_filename, file_type)


def csv_rows(query):
    row = query.first()
    header = row.keys()
    rows = []
    for item in query.all():
        rows.append(list(item))
    return dict(header=header,
                rows=rows)


def csv_response(request, value, filename=None):
    if not filename:
        filename = get_random_string(20)+".csv"
    response = request.response
    response.content_type = 'text/csv'
    # response.content_disposition = 'attachment;filename=' + filename
    response.content_disposition = 'filename=' + filename
    if sys.version_info < (3,):
        import StringIO
        fout = StringIO.StringIO()
    else:
        fout = io.StringIO()

    fcsv = csv.writer(fout, delimiter=',', quotechar='"',
                      quoting=csv.QUOTE_MINIMAL)
    fcsv.writerow(value.get('header', []))
    fcsv.writerows(value.get('rows', []))
    response.write(fout.getvalue())
    return response


def terbilang(bil):
    angka = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam",
             "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    hasil = " "
    n = int(bil)
    if 0 <= n <= 11:
        hasil = hasil + angka[n]
    elif n < 20:
        hasil = terbilang(n % 10) + " Belas"
    elif n < 100:
        hasil = terbilang(n / 10) + " Puluh" + terbilang(n % 10)
    elif n < 200:
        hasil = " Seratus" + terbilang(n - 100)
    elif n < 1000:
        hasil = terbilang(n / 100) + " Ratus" + terbilang(n % 100)
    elif n < 2000:
        hasil = " Seribu" + terbilang(n - 1000)
    elif n < 1000000:
        hasil = terbilang(n / 1000) + " Ribu" + terbilang(n % 1000)
    elif n < 1000000000:
        hasil = terbilang(n / 1000000) + " Juta" + terbilang(n % 1000000)
    else:
        hasil = terbilang(n / 1000000000) + " Miliar" + \
            terbilang(n % 1000000000)
    return hasil


def ods_export(request, filename, file_type):
    settings = get_settings()
    if 'unoconv_py' in settings and settings['unoconv_py']:
        if 'unoconv_bin' in settings and settings['unoconv_bin']:
            unoconv_py = settings['unoconv_py']
            unoconv_bin = settings['unoconv_bin']
            f = '.'.join([filename, 'ods'])
            subprocess.call([unoconv_py, unoconv_bin, '-f', file_type, f])
            out_filename = '.'.join([filename, file_type])
            with open(out_filename, 'rb') as f:
                return file_response(request, f, out_filename, file_type)


# use
# pdf_compress("/tmp/original.pdf", "/tmp/compressed.tmp")
# return None
def pdf_compress(original_filename, compressed_filename=None):
    if compressed_filename is None:
        ori_dir = os.path.dirname(original_filename)
        ori_filename = os.path.basename(original_filename)
        filenames = ori_filename.split('.')
        ext = filenames[-1]
        filename = "".join(filenames[:-1])
        compressed_filename = os.path.join(
            ori_dir, f"{filename}_compressed.{ext}")

    reader = PdfReader(original_filename)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    if reader.metadata is not None:
        writer.add_metadata(reader.metadata)

    with open(compressed_filename, "wb") as fp:
        writer.write(fp)

    return compressed_filename

# use:
# tmp_reports(module_dirname="pbb/pendataan")
# tmp_reports(settings=get_settings(), module_dirname="pbb/pendataan")
# tmp_reports(settings=get_settings(), tmp_path="/home/user/tmp", module_dirname="pbb/pendataan")
# return "string of path"


def tmp_reports(settings=None, tmp_path=None, module_dirname=None):
    default_tmp = '/tmp'

    if settings is None:
        settings = get_settings()

    if not settings:
        if tmp_path is None:
            tmp_path = default_tmp
    else:
        if tmp_path is None:
            tmp_path = 'tmp_report' in settings and settings['tmp_report'] or default_tmp

    if module_dirname:
        tmp_path = os.path.join(tmp_path, module_dirname)

    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

    return tmp_path


class Item(object):
    pass


# Jasper Processor
# class BaseView(object):
    # def __init__(self, request):
    # super().__init__(request)
    # self.user_id = self.req.user.id
    # self.user_admin = self.req.has_permission('pjdl-admin') \
    #     or self.req.has_permission('admin') or False
    # self.report_folder = "master"
    # self._file = None
    # self.report_path = MODULE_CLASS.report_path

    # @property
    # def report_file(self):
    #     return os.path.join(self.report_path, self.report_folder, self._file)

    # @report_file.setter
    # def report_file(self, value):
    #     self._file = value

    # def get_report_filter(self, values, pars, opts=True):
    #     # pars = p.split(":")
    #     if opts:
    #         if pars[1] not in values:
    #             par = len(pars) > 3 and pars[3] or pars[1]
    #             raise HTTPNotFound(f"Parameter {par} belum diisi")
    #     # if pars[1].find("customer")>-1:
    #     # raise Exception("X")

    #     if pars[1] in values:
    #         vals = values[pars[1]]
    #         if pars[2] == "str":
    #             self.params[pars[1]] = str(vals)
    #             if not opts:
    #                 self.kondisi = f"{self.kondisi} AND {pars[0]}='{vals}'"
    #             vals = f"'{vals}'"
    #             self.qry = self.qry.filter(
    #                 func.CAST(PjdlReportItems.params[pars[1]], String) == f'"{vals}"')
    #         elif pars[2] == "int":
    #             self.params[pars[1]] = int(vals)
    #             if not opts:
    #                 self.kondisi = f"{self.kondisi} AND {pars[0]}={vals}"
    #             vals = f"{vals}"
    #             self.qry = self.qry.filter(
    #                 func.CAST(PjdlReportItems.params[pars[1]], String) == f'{vals}')
    #         elif pars[2] in ["dMy", "ymd", "dmy"]:
    #             vals = date_from_str(vals)
    #             fc = getattr(opensipkd.tools, pars[2])
    #             vals = f"{fc(vals)}"
    #             self.params[pars[1]] = vals
    #             self.qry = self.qry.filter(
    #                 func.CAST(PjdlReportItems.params[pars[1]], String) == f'"{vals}"')
    #             if not opts:
    #                 self.kondisi = f"{self.kondisi} AND {pars[0]}='{vals}'"
    #         else:
    #             raise Exception(f"Belum ada fungsi {pars[2]}")
    #         # if pars[1]!="tgl_cetak":

    # def jasper_response(self, **kwargs):
    #     from opensipkd.base.tools.report import jasper_export
    #     output_formats = kwargs.get("output_formats", ["pdf"])
    #     force = kwargs.get("force", False)

    #     # Menghindari temporary file dalam module aplikasi
    #     out_path = get_params("pjdl_report_files", '/tmp/pjdl/reports')
    #     out_path = os.path.join(out_path, "out")
    #     if not os.path.exists(out_path):
    #         os.makedirs(out_path)

    #     # Ambil-nama-report dari tabel report
    #     rpt_kode = os.path.basename(self.report_file)
    #     row = PjdlReports.query_kode(rpt_kode).first()
    #     if not row:
    #         return HTTPNotFound(f"File report {rpt_kode} belum terdaftar")

    #     # Check data pada report yang sudah dibuat
    #     self.qry = PjdlReportItems.query().filter(PjdlReportItems.report_id == row.id)

    #     self.params = {}
    #     self.kondisi = ""
    #     if row and row.params:
    #         par = row.params.replace('\r', '').replace('\n', '')
    #         par = par.split(",")
    #         if par:
    #             values = kwargs.get("values", {})
    #             for p in par:
    #                 if p.startswith('['):
    #                     # optional parameter
    #                     p = p.strip('[').strip(']')
    #                     pars = p.split(":")
    #                     _logging.debug(f"pars: {pars}")
    #                     self.get_report_filter(values, pars, False)
    #                 else:
    #                     pars = p.split(":")
    #                     _logging.debug(f"pars: {pars}")
    #                     if pars[1] not in values:
    #                         par = len(pars) > 3 and pars[3] or pars[1]
    #                         return HTTPNotFound(f"Parameter {par} Belum Diisi")
    #                     self.get_report_filter(values, pars)

    #             _logging.debug(f"kondisinya: {self.kondisi}")
    #             self.params["kondisi"] = self.kondisi

    #     self.qry = self.qry.filter(
    #         func.CAST(
    #             PjdlReportItems.params["output_formats"], String) == f'"{output_formats}"')

    #     items = self.qry.first()

    #     if items and not force:
    #         file_name = os.path.join(out_path, items.file_name)
    #         if not os.path.exists(os.path.join(out_path, file_name)):
    #             force = True
    #     else:
    #         force = True

    #     if force:
    #         self.params.update(MODULE_CLASS.report_params)
    #         _logging.debug(f"parameter: {self.params}")
    #         file_name = jasper_export(
    #             self.report_file, out_path, parameters=self.params,
    #             output_formats=output_formats)[0]

    #         if not items:
    #             items = PjdlReportItems()
    #             items.report_id = row.id
    #             self.params["output_formats"] = output_formats
    #             items.params = self.params
    #             _logging.debug(f"parameter: {self.params}")
    #         items.file_name = os.path.basename(file_name)
    #         flush(items)

    #     return file_response(self.req, filename=file_name)
