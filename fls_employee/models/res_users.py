from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_fls_geo_ids = fields.Many2many('fls.geo', string='Allowed FLS Geo')
