from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_service_invoicing_policy = fields.Selection(string='Service Invoicing Policy', selection=[
        ('ordered_prepaid','Prepaid/Fixed Price'), 
        ('delivered_timesheet','Based on Timesheets'), 
        ('delivered_milestones','Based on Milestones'), 
        ('delivered_manual','Based on Delivered Quantity (Manual)')], compute='_compute_product_service_invoicing_policy', store=True, readonly=True)

    @api.depends('product_id')
    def _compute_product_service_invoicing_policy(self):
        for line in self:
            line.product_service_invoicing_policy = line.product_id.service_policy
