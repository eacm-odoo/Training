from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class CustomPortalController(CustomerPortal):

    @http.route(['/my/invoices/<int:invoice_id>'], type='http', auth="public", website=True)
    def portal_my_invoice_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
        try:
            invoice_sudo = self._document_check_access('account.move', invoice_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            if invoice_sudo.company_id.custom_invoices:
                return self._show_report(model=invoice_sudo, report_type=report_type, report_ref='fls_reports.fls_report_invoice_doc', download=download)
            else:
                return self._show_report(model=invoice_sudo, report_type=report_type, report_ref='account.account_invoices', download=download)
        values = self._invoice_get_page_view_values(invoice_sudo, access_token, **kw)
        return request.render("account.portal_invoice_page", values)
