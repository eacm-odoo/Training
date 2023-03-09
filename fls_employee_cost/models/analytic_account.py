from odoo import fields, models, _, api
from datetime import date

import logging
_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    amount = fields.Monetary(string="Amount", copy=False)
    
    @api.depends('is_adjusted', 'unit_amount')
    def _compute_amount(self):
        usd_currency = self.env['res.currency'].search([('name','=','USD')])
        for line in self:
        if not line.is_adjusted:
            conversion_rate = 1
            if usd_currency != line.employee_id.currency_id:
                conversion_rate = self.env['res.currency']._get_conversion_rate(line.employee_id.currency_id,line.currency_id,line.company_id,date.today().strftime("%m/%d/%y"))
            line.amount = (-line.unit_amount)*line.employee_id.hourly_cost*conversion_rate
        else:
            line.amount = 0
                
    @api.onchange('product_id', 'product_uom_id', 'unit_amount', 'currency_id', 'is_adjusted')
    def on_change_unit_amount(self):
        usd_currency = self.env['res.currency'].search([('name','=','USD')])
        super(AccountAnalyticLine, self).on_change_unit_amount()
        if self.is_adjusted:
            self.amount = 0.0
        _logger.info("\n")
        _logger.info(self.amount)
        _logger.info("\n")