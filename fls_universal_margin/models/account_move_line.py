from odoo import api, fields, models  

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
        
    exchange_rate_usd = fields.Float(string='Exchange Rate USD', compute='_compute_exchange_rate_usd', store=True)
    exchange_rate_company_currency = fields.Float(string='Exchange Rate Company Currency', compute='_compute_exchange_rate_company', store=True)
    so_item_id = fields.Many2one('sale.order.line', string='Sale Order Item', compute='_compute_so_item', store=True)
    fls_partner_employee_id = fields.Many2one('hr.employee', string='FLS Employee', compute='_compute_fls_partner_employee_id', store=True)


    @api.depends('partner_id')
    def _compute_fls_partner_employee_id(self):
        for line in self:
            line.fls_partner_employee_id = line.partner_id.employee_id if line.partner_id else False

    @api.depends('sale_line_ids')
    def _compute_so_item(self):
        for line in self:
            line.so_item_id = line.sale_line_ids[0] if line.sale_line_ids else False

    @api.depends('currency_id', 'date')
    def _compute_exchange_rate_usd(self):
        usd_currency = self.env['res.currency'].search([('name','=','USD')], limit=1) 
        for line in self:
            line.exchange_rate_usd = 1 if not line.exchange_rate_usd else line.exchange_rate_usd
            if line.currency_id == usd_currency:
                continue

            if line.currency_id and line.company_id and line.date:
                line.exchange_rate_usd = self.env['res.currency']._get_conversion_rate(line.currency_id,usd_currency,line.company_id,line.date.strftime("%m/%d/%y"))

    @api.depends('currency_id', 'date', 'company_id')
    def _compute_exchange_rate_company(self):
        for line in self:
            company_currency = line.company_id.currency_id
            line.exchange_rate_company_currency = 1 if not line.exchange_rate_company_currency else line.exchange_rate_company_currency
            if line.currency_id == company_currency:
                continue

            if line.currency_id and line.company_id and line.date:
                line.exchange_rate_company_currency = self.env['res.currency']._get_conversion_rate(line.currency_id,company_currency,line.company_id,line.date.strftime("%m/%d/%y")) or 1
