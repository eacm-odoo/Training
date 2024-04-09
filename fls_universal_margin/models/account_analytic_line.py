from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    multiplier = fields.Float(string='Multiplier', default=0.0)
    sol_product_service_invoicing_policy = fields.Selection(string='Order Item Service Invoicing Policy', selection=[
        ('ordered_prepaid','Prepaid/Fixed Price'), 
        ('delivered_timesheet','Based on Timesheets'), 
        ('delivered_milestones','Based on Milestones'), 
        ('delivered_manual','Based on Delivered Quantity (Manual)')], store=True)
    exchange_rate_usd = fields.Float(string='Exchange Rate USD', compute='_compute_exchange_rate_usd', store=True)
    exchange_rate_company_currency = fields.Float(string='Exchange Rate Company Currency', compute='_compute_exchange_rate_company', store=True)


    @api.depends('amount', 'currency_id', 'date')
    def _compute_exchange_rate_usd(self):
        usd_currency = self.env['res.currency'].search([('name','=','USD')], limit=1) 
        for line in self:
            line.exchange_rate_usd = 1 if not line.exchange_rate_usd else line.exchange_rate_usd
            if line.currency_id == usd_currency:
                continue

            if line.currency_id and line.company_id and line.date:
                currency_conversion_rate = self.env['res.currency']._get_conversion_rate(line.currency_id,usd_currency,line.company_id,line.date.strftime("%m/%d/%y"))
                line.exchange_rate_usd = currency_conversion_rate


    @api.depends('currency_id', 'date', 'company_id')
    def _compute_exchange_rate_company(self):
        for line in self:
            company_currency = line.company_id.currency_id
            line.exchange_rate_company_currency = 1 if not line.exchange_rate_company_currency else line.exchange_rate_company_currency
            if line.currency_id == company_currency:
                continue

            if line.currency_id and line.company_id and line.date:
                line.exchange_rate_company_currency = self.env['res.currency']._get_conversion_rate(line.currency_id,company_currency,line.company_id,line.date.strftime("%m/%d/%y")) or 1
