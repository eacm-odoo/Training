from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ref = fields.Char("Ref")