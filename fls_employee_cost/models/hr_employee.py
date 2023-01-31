from odoo import fields, models, api
from datetime import date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    full_cost = fields.Float(string="Full Cost in USD", compute="_compute_full_cost", store=True)

    @api.depends('contract_ids', 'address_home_id')
    def _compute_full_cost(self):
        done = []
        usd_currency = self.env['res.currency'].search([('name','=','USD')])
        for employee in self:
            if employee.id not in done:
                full_cost = 0
                all_employee_ids = employee.address_home_id.employee_ids
                for unique_employee in all_employee_ids:
                    contract_count = 0
                    unique_employee.full_cost = 0
                    usd_conversion_rate = self.env['res.currency']._get_conversion_rate(unique_employee.company_id.currency_id,usd_currency,unique_employee.company_id,date.today().strftime("%m/%d/%y"))
                    for contract in unique_employee.contract_ids:
                        if contract.state == 'open':
                            full_cost += contract.burden_wage_hourly*usd_conversion_rate
                            contract_count += 1
                for unique_employee in all_employee_ids:
                    unique_employee.full_cost = full_cost
                    done.append(unique_employee.id)