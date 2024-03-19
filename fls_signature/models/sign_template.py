from odoo import fields, models


class SignRequest(models.Model):
    _inherit = 'sign.template'

    assign_partner_to_doc = fields.Boolean(string='Assign Partner to generated document', default=False)
