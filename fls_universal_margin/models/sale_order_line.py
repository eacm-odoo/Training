from odoo import fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_service_invoicing_policy = fields.Selection(string='Service Invoicing Policy', selection=[
        ('ordered_prepaid','Prepaid/Fixed Price'), 
        ('delivered_timesheet','Based on Timesheets'), 
        ('delivered_milestones','Based on Milestones'), 
        ('delivered_manual','Based on Delivered Quantity (Manual)')])
