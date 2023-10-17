from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'
    custom_invoices = fields.Boolean(string="Custom Report Templates for Invoices")