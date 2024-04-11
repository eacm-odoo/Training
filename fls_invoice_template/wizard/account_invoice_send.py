from odoo import fields, models


class AccountInvoiceSend(models.TransientModel):
    _inherit = "account.invoice.send"

    pdf_report_id = fields.Many2one("ir.actions.report", string="PDF Template", domain=[("model", "=", "account.move")])

    def _send_email(self):
        return super(AccountInvoiceSend, self.with_context(pdf_report_id=self.pdf_report_id))._send_email()
