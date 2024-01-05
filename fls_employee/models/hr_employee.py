from odoo import fields, models, api, _
from odoo.exceptions import UserError

import re


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_margin_id = fields.Many2one('hr.employee.margin', string='Recent Margin')
    work_country_id = fields.Many2one('res.country', string='Work Country', related='address_id.country_id', store=True)
    fls_geo_id = fields.Many2one('fls.geo', string='FLS Geo')

    timesheet_ids = fields.One2many('account.analytic.line', 'employee_id', string='Timesheets', domain=[('so_line.product_id.service_policy', '!=', 'delivered_timesheet')])
    # timesheet_ids = fields.One2many('account.analytic.line', 'employee_id', string='Timesheets', domain=[('so_line.product_id.service_policy', '!=', 'delivered_timesheet')])
    sol_invoice_ids = fields.Many2many('account.move.line', string='SOL Invoices', compute='_compute_sol_invoice_ids', store=True)
    revenue_on_date = fields.Float(string='Revenue On Date', compute='_compute_revenue_on_date')

    @api.depends('timesheet_ids')
    def _compute_sol_invoice_ids(self):
        for employee in self:
            employee.sol_invoice_ids = employee.timesheet_ids.mapped('so_line.invoice_lines.move_id.line_ids')


    @api.depends('sol_invoice_ids')
    def _compute_revenue_on_date(self, date_from=None, date_to=None):
        date_from = fields.Date.from_string('2024-01-01')
        date_to = fields.Date.today()
        for employee in self:
            revenue = 0
            for timesheet in employee.timesheet_ids:
                sol =  timesheet.so_line
                filtered_invoice_lines = sol.invoice_lines.filtered(
                    # lambda aml: aml.move_id.date.month == date_from.month and aml.move_id.date.year == date_from.year
                    lambda aml: aml.move_id.date.month == date_from.month and aml.move_id.date.year == 2023
                )
                for aml in filtered_invoice_lines:
                    revenue += aml.price_subtotal * aml.conversion_rate
                
                filtered_timesheet_ids = sol.timesheet_ids.filtered(
                    # lambda aal: aal.date.month == date_from.month and aal.date.year == date_from.year)
                    lambda aal: aal.date.month == date_from.month and aal.date.year == 2023)
                
                employee_timesheet_counter = len([aal for aal in filtered_timesheet_ids if aal.employee_id.id == employee.id])
                revenue /= len(filtered_timesheet_ids.employee_id.ids) or 1
                revenue /= employee_timesheet_counter or 1

            employee.revenue_on_date = revenue

    def _normalize_name(self, name):
        return re.sub(' +', ' ', name).strip() if name else name

    @api.model_create_multi
    def create(self, vals_list):
        for record in vals_list:
            name = record.get('name')
            normalized_name = self._normalize_name(name)
            domain = ['|', ('name', '=ilike', normalized_name), ('name', 'ilike', name)]
            if self.search(domain, limit=1):
                raise UserError(_('An employee with a similar name already exists.'))
                
        return super(HrEmployee, self).create(vals_list)
