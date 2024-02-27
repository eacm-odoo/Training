from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountAnalyticLineSplit(models.TransientModel):
    _name = 'account.analytic.line.split'
    _description = 'Account Analytic Line Split'

    work_hour_limit = fields.Float(string='Regular Hours', required=True, default=8.0)
    account_analytic_line_ids = fields.Many2many('account.analytic.line', string='Timesheets', compute='_compute_account_analytic_line_ids')

    def _compute_account_analytic_line_ids(self):
        self.ensure_one()
        self.account_analytic_line_ids = self.env['account.analytic.line'].browse(self._context.get('active_ids'))

    def button_confirm(self):
        self.ensure_one()
        user_in_fls_operational_manager = self.env.user.has_group('__export__.res_groups_70_08a20b3f') 
        user_is_project_manager = all([True if user.id == self.env.user.id else False for user in self.account_analytic_line_ids.project_id.user_id])
        is_own_timesheets = all([True if aal.employee_user_id.id == self.env.user.id else False for aal in self.account_analytic_line_ids])

        lines_to_split = self.account_analytic_line_ids.filtered(lambda aal: aal.unit_amount > self.work_hour_limit)
        for line in lines_to_split:
            line.copy({
                'unit_amount': line.unit_amount - self.work_hour_limit,
                'time_type': 'overtime'
            }) 
            line.write({
                'unit_amount': self.work_hour_limit,
                'time_type': 'regular'
            })
        return {'type': 'ir.actions.act_window_close'}
