from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_policy = fields.Selection('_selection_service_policy', string="Service Invoicing Policy", compute='_compute_service_policy', inverse='_inverse_service_policy', store=True)
    