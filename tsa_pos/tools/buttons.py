import pyramid.i18n as i18
from deform.form import Button
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('button')

btn_add = Button('add', title=_('Add'), css_class="btn-success")
btn_view = Button('view', title=_('View'), css_class="btn-info")
btn_edit = Button('edit', title=_('Edit'), css_class="btn-success")
btn_delete = Button('delete', title=_('Delete'), css_class="btn-danger")
btn_copy = Button('copy', title=_('Copy'), css_class="btn-success")
btn_save = Button('save', title=_('Save'), css_class="btn-primary")
btn_force = Button('force', title=_('Force'), css_class="btn-info")
btn_upload = Button('upload', title=_('Upload'), css_class="btn-info")
btn_filter = Button('filter', title=_('Filter'), css_class="btn-info")
btn_cancel = Button('cancel', title=_('Cancel'), css_class="btn-warning")
btn_reset = Button('reset', title=_('Reset'), css_class="btn-warning",
                   type="reset")
btn_recall = Button('recall', title=_('Recall'), css_class="btn-info",
                    type="submit")
btn_draft = Button('draft', title=_('Draft'), css_class="btn-info",
                   type="submit")

btn_close = Button('close', title=_('Close'), css_class="btn-danger")
btn_print = Button('print', title=_('Print'), css_class="btn-info",
                   type="button")
btn_pdf = Button('pdf', title='PDF', css_class="btn-info", type="button")
btn_csv = Button('csv', title='CSV', css_class="btn-info", type="button")
btn_xls = Button('xls', title='XLS', css_class="btn-info", type="button")
btn_txt = Button('txt', title='TXT', css_class="btn-info", type="button")

btn_label = Button('label', title=_('Print Label'), css_class="btn-info",
                   type="button")
btn_print_ttr = Button('ttr', title=_('Receive'), css_class="btn-info",
                       type="button")
btn_barcode = Button('barcode', title=_('Barcode'), css_class="btn-success",
                     type="button")
btn_qrcode = Button('qrcode', title=_('QRcode'), css_class="btn-success",
                    type="button")
btn_barcode_nop = Button('barcode_nop', title=_('Barcode NOP'),
                         css_class="btn-info", type="button")

btn_inquiry = Button('inquiry', title=_('Inquiry'), css_class="btn-info",
                     type="submit")
btn_invoice = Button('invoice', title=_('Invoice'), css_class="btn-info",
                     type="submit")
btn_map = Button('map', title=_('MAP'), css_class="btn-info", type="submit")
btn_payment = Button('payment', title=_('Payment'), css_class="btn-success",
                     type="submit")

btn_accept = Button('accept', title=_('Accept'), css_class="btn-success")
btn_reject = Button('reject', title=_('Reject'), css_class="btn-danger")

btn_prev = Button('prev', title=_('Back'), css_class="btn-success")
btn_next = Button('next', title=_('Next'), css_class="btn-success")

btn_send = Button('send', title=_('Send'), css_class="btn-success")
btn_search = Button('search', title=_('Search'), css_class="btn-success")

btn_proses = Button('proses', title=_('Process'), css_class="btn-info")

inquiry_button = [btn_inquiry, btn_cancel]
payment_button = [btn_payment, btn_cancel]

print_button = [btn_print, btn_cancel]
proses_button = [btn_proses, btn_cancel]

save_buttons = [btn_save, btn_cancel]
update_buttons = [btn_add, btn_edit, btn_delete, btn_close]
flow_buttons = [btn_prev, btn_accept, btn_reject, btn_next]
delete_buttons = [btn_delete, btn_cancel]
flow_1_buttons = [btn_next, btn_cancel]
force_buttons = [btn_force, btn_cancel]
flow_2_buttons = [btn_prev, btn_next, btn_cancel]
pdf_txt_buttons = [btn_pdf, btn_txt, btn_close]
pdf_buttons = [btn_pdf, btn_close]

btn_login = Button('login', title=_('Login'), css_class="btn-success")
btn_register = Button('register', title=_('Register'), css_class="btn-success")
btn_password = Button('password', title=_('Change Password'),
                      css_class="btn-danger")
btn_lost = Button('lost', title=_('Lost Password'), css_class="btn-danger")
btn_yes = Button('yes', title=_('Yes'), css_class="btn-success")
btn_no = Button('no', title=_('No'), css_class="btn-danger")


# karena error serve, sy tambahkan ini
btn_post = Button('post', title=_('Post'), css_class="btn-info", type="button")
btn_unpost = Button('unpost', title=_('UnPost'),
                    css_class="btn-info", type="button")
btn_check = Button('check', title=_('Check'),
                   css_class="btn-info", type="button")
