from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    full_cost = fields.Float(string="Full Cost in USD", compute="_compute_full_cost", store=True)

    @api.depends('contract_ids','contract_ids.burden_wage_hourly','contract_ids.state')
    def _compute_full_cost(self):
        for employee in self:
            employee.full_cost = 0
            for contract in employee.contract_ids:
                if contract.state == 'open':
                    employee.full_cost += contract.burden_wage_hourly