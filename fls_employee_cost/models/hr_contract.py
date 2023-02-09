from odoo import fields, models, api
from datetime import date


class HrContract(models.Model):
    _inherit = 'hr.contract'

    burden_rate = fields.Float(string="Burden Rate")
    burden_wage = fields.Float(string="Burdened Wage", compute="_compute_burden_wage")
    burden_wage_hourly = fields.Float(string="Burdened Wage Hourly USD", compute="_compute_burden_wage")

    @api.depends('wage','wage_type','hourly_wage','burden_rate', 'employee_id', 'company_id', 'company_id.annual_hours')
    def _compute_burden_wage(self):
        usd_currency = self.env['res.currency'].search([('name','=','USD')])
        for contract in self:
            contract.burden_wage = 0
            contract.burden_wage_hourly = 0
            annual_contract_hours = contract.company_id.annual_hours/12*11/40*contract.resource_calendar_id.week_hours
            if contract.wage_type == 'monthly':
                contract.burden_wage = contract.wage + contract.burden_rate*contract.wage
            elif contract.wage_type == 'hourly':
                monthly_wage = contract.hourly_wage*annual_contract_hours/12
                contract.burden_wage = monthly_wage + contract.burden_rate*monthly_wage
            if annual_contract_hours > 0:
                usd_conversion_rate = self.env['res.currency']._get_conversion_rate(contract.company_id.currency_id,usd_currency,contract.company_id,date.today().strftime("%m/%d/%y"))
                contract.burden_wage_hourly = contract.burden_wage*12/annual_contract_hours*usd_conversion_rate