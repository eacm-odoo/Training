from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    annual_hours = fields.Integer(string='Total Annual Hours')
