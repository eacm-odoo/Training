from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    vendor = fields.Boolean(string="Vendor")
