from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    burden_rate = fields.Float(string="Burden Rate")
    burden_wage = fields.Float(string="Burdened Wage", compute="_compute_burden_wage")
    burden_wage_hourly = fields.Float(string="Burdened Wage Hourly", compute="_compute_burden_wage_hourly")

    @api.depends('wage','burden_rate')
    def _compute_burden_wage(self):
        for contract in self:
            contract.burden_wage = contract.wage + contract.burden_rate*contract.wage

    @api.depends('wage','burden_rate', 'employee_id')
    def _compute_burden_wage_hourly(self):
        for contract in self:
            contract.burden_wage_hourly = 0
            burden_wage = contract.wage + contract.burden_rate*contract.wage
            annual_contract_hours = contract.employee_id.company_id.annual_hours/12*11/40*contract.resource_calendar_id.week_hours
            if annual_contract_hours > 0:
                contract.burden_wage_hourly = burden_wage*12/annual_contract_hours