from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import AccessError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    is_approved = fields.Boolean(string="Is Approved", readonly=False)
    project_manager_id = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id', store=True)
    timesheet_manager_id = fields.Many2one('res.users', string='Resource Manager', related='employee_id.timesheet_manager_id', store=True)
    employee_user_id = fields.Many2one('res.users', string='Employee User', related='employee_id.user_id', store=True)

    @api.constrains('is_approved')
    def _check_approval(self):
        for line in self:
            if self.env.user.id != line.timesheet_manager_id.id and self.env.user.id != line.project_manager_id.id and line.is_approved and not self.user_has_groups('hr_timesheet.group_timesheet_manager'):
                raise AccessError("You cannot approve unless you're Project Manager, Resource Manager, or Admin!")

    @api.depends_context('uid')
    def _compute_can_validate(self):
        is_manager = self.user_has_groups('hr_timesheet.group_timesheet_manager')
        is_approver = self.user_has_groups('hr_timesheet.group_hr_timesheet_approver')
        for line in self:
            if is_manager or (is_approver and self.env.user.id == line.timesheet_manager_id.id):
                line.user_can_validate = True
            else:
                line.user_can_validate = False
                
    def check_access_rule(self, operation):
        if operation in ['create','write'] and all(self.mapped('user_can_validate')):
            return
        return super(AccountAnalyticLine, self).check_access_rule(operation)
        
    def check_access_rights(self, operation, raise_exception=True):
        for line in self:
            # No create or write of any record before freeze date
            freeze = self.env['ir.config_parameter'].sudo().get_param('fls_timesheet_validation.freeze_timesheets')
            if operation in ['create','write'] and freeze:
                freeze_day = int(self.env['ir.config_parameter'].sudo().get_param('fls_timesheet_validation.freeze_day') or 1)
                freeze_month = int(self.env['ir.config_parameter'].sudo().get_param('fls_timesheet_validation.freeze_month') or 1)
                freeze_year = int(self.env['ir.config_parameter'].sudo().get_param('fls_timesheet_validation.freeze_year') or 2000)
                freeze_date = date(freeze_year,freeze_month,freeze_day)
                if line.date and line.date < freeze_date:
                    raise AccessError("All timesheet records are frozen before {}".format(freeze_date))
            # No access to timsheets when validated
        return super(AccountAnalyticLine, self).check_access_rights(operation, raise_exception)

    def write(self, vals):
        # User cannot modify timesheet to have frozen date
        freeze = self.env['ir.config_parameter'].sudo().get_param('fls_timesheet_validation.freeze_timesheets')
        if 'date' in vals and freeze:
            freeze_day = int(self.env['ir.config_parameter'].sudo().get_param('fls_timesheet_validation.freeze_day') or 1)
            freeze_month = int(self.env['ir.config_parameter'].sudo().get_param('fls_timesheet_validation.freeze_month') or 1)
            freeze_year = int(self.env['ir.config_parameter'].sudo().get_param('fls_timesheet_validation.freeze_year') or 2000)
            freeze_date = date(freeze_year,freeze_month,freeze_day)
            if datetime.strptime(vals['date'],'%Y-%m-%d').date() < freeze_date:
                raise AccessError("All timesheet records are frozen before {}".format(freeze_date))
        return super(AccountAnalyticLine, self).write(vals)
