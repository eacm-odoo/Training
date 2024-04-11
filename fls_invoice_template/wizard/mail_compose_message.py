from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _action_send_mail(self, auto_commit=False):
        pdf_report_id = self._context.get("pdf_report_id", False)
        if pdf_report_id:
            pdf_report_id._render_qweb_pdf(pdf_report_id.report_name, self.res_id)
            record = self.env[self.render_model].browse(self.res_id)
            self.attachment_ids = pdf_report_id.retrieve_attachment(record)
        return super()._action_send_mail(auto_commit)
