from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    cost_usd = fields.Float(string="Cost USD", compute='_compute_cost_usd', store=True)
    revenue_usd = fields.Float(string="Revenue USD", compute='_compute_revenue_usd', store=True)

    @api.depends('amount', 'currency_id')
    def _compute_cost_usd(self):
        usd_currency = self.env['res.currency'].search([('name','=','USD')], limit=1) 
        for line in self:
            line.cost_usd = 0
            if line.currency_id and line.company_id and line.date:
                currency_conversion_rate = self.env['res.currency']._get_conversion_rate(line.currency_id,usd_currency,line.company_id,line.date.strftime("%m/%d/%y"))
                line.cost_usd = line.amount * currency_conversion_rate

    @api.depends(
        'date', 
        'unit_amount', 
        'so_line.currency_id', 
        'so_line.price_unit', 
        'so_line.product_id', 
        'so_line.product_id.service_policy', 
        'so_line.order_id.company_id')
    def _compute_revenue_usd(self):
        usd_currency = self.env['res.currency'].search([('name','=','USD')], limit=1)
        for line in self:
            line.revenue_usd = 0
            if line.date and line.so_line and line.so_line.currency_id and line.so_line.order_id and line.so_line.order_id.company_id:
                currency_conversion_rate = self.env['res.currency']._get_conversion_rate(line.so_line.currency_id,usd_currency,line.so_line.order_id.company_id,line.date.strftime("%m/%d/%y"))
                if line.so_line.product_id.service_policy == 'delivered_timesheet':
                    line.revenue_usd = line.so_line.price_unit * line.unit_amount * currency_conversion_rate
                    
