from odoo import models


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        session_info = super(Http, self).session_info()
        session_info['max_file_upload_size'] = self.env['ir.config_parameter'].sudo().get_param('fls_attachment.attachment_limit') * 1024 ** 2 # given in MB, convert to bytes
        return session_info

