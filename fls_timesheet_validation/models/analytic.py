from odoo import models, fields, api
from datetime import date
from odoo.exceptions import AccessError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    is_approved = fields.Boolean(string="Is Approved")
    project_manager_id = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id', store=True)
    timesheet_manager_id = fields.Many2one('res.users', string='Resource Manager', related='employee_id.timesheet_manager_id', store=True)
    employee_user_id = fields.Many2one('res.users', string='Employee User', related='employee_id.user_id', store=True)

    @api.depends_context('uid')
    def _compute_can_validate(self):
        is_manager = self.user_has_groups('hr_timesheet.group_timesheet_manager')
        is_approver = self.user_has_groups('hr_timesheet.group_hr_timesheet_approver')
        for line in self:
            if is_manager or (is_approver and self.env.user.id == line.timesheet_manager_id.id):
                line.user_can_validate = True
            else:
                line.user_can_validate = False
    
    @api.model_create_multi
    def create(self, vals_list):
        freeze = self.env['ir.config_parameter'].sudo().get_param('fls_timesheet_validation.freeze_timesheets')
        freeze_day = int(self.env['ir.config_parameter'].sudo().get_param('fls_timesheet_validation.freeze_day'))
        freeze_date = date.today().replace(day=freeze_day)
        expected_date = date.today().replace(year=2000)
        if date in vals_list:
            expected_date = vals_list['date']
        if self.is_timesheet and freeze and expected_date < freeze_date:
            raise AccessError("Cannot create a new record before this date: {}".format(freeze_date))
        return super(AccountAnalyticLine, self).create(vals_list)

    def write(self, vals):
        freeze = self.env['ir.config_parameter'].sudo().get_param('fls_timesheet_validation.freeze_timesheets')
        freeze_day = int(self.env['ir.config_parameter'].sudo().get_param('fls_timesheet_validation.freeze_day'))
        freeze_date = date.today().replace(day=freeze_day)
        expected_date = self.date
        if date in vals:
            expected_date = vals['date']
        if self.is_timesheet and freeze and (self.date < freeze_date or expected_date < freeze_date):
            raise AccessError("Cannot create a new record before this date: {}".format(freeze_date))
        return super(AccountAnalyticLine, self).write(vals)