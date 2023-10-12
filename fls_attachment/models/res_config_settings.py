from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    attachment_limit = fields.Float(
        string='Attachment Limit',
        config_parameter='fls_attachment.attachment_limit',
        help='Maximum size of attachment in MB. Set 0 to disable limit.',
        default=0.0
    )