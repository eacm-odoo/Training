from odoo import models, fields, api, _


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def get_mail_values(self, res_ids):
        res = super(MailComposeMessage, self).get_mail_values(res_ids)

        if self.template_id.use_text:
            for r in res:
                res[r]['use_text'] = self.template_id.use_text
                res[r]['email_layout_xmlid'] = 'fls_mail_plain_body.no_template_template'

        return res
