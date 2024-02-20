from odoo import models, fields, api, _
from odoo.addons.website.tools import text_from_html

class MailTemplate(models.Model):
    _inherit = 'mail.template'

    use_text = fields.Boolean(string='Use Plain Text', default=False)
