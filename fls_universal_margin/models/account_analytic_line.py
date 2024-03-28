from odoo import fields, models

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    multiplier = fields.Float(string='Multiplier', default=0.0)
    sol_product_service_invoicing_policy = fields.Selection(string='Order Item Service Invoicing Policy', selection=[
        ('ordered_prepaid','Prepaid/Fixed Price'), 
        ('delivered_timesheet','Based on Timesheets'), 
        ('delivered_milestones','Based on Milestones'), 
        ('delivered_manual','Based on Delivered Quantity (Manual)')], store=True)
