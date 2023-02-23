from odoo import fields, models, api
from datetime import date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    full_cost = fields.Float(string="Full Cost in USD", compute="_compute_full_cost", store=True)
    hourly_cost = fields.Monetary('Hourly Cost', currency_field='currency_id',groups="hr.group_hr_user", compute="_compute_full_cost", store=True, readonly=False)

    @api.depends('contract_ids','contract_ids.burden_wage_hourly','contract_ids.state')
    def _compute_full_cost(self):
        for employee in self:
            employee.full_cost = 0
            for contract in employee.contract_ids:
                if contract.state == 'open':
                    employee.full_cost += contract.burden_wage_hourly
            employee.hourly_cost = employee.full_cost