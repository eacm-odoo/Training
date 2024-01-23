from odoo import models, fields, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    prevent_so_line_update = fields.Boolean(string="Prevent Sale Order Line Update", default=False)

    @api.depends('task_id.sale_line_id', 'project_id.sale_line_id', 'employee_id', 'project_id.allow_billable')
    def _compute_so_line(self):
        for timesheet in self.filtered(lambda t: not t.is_so_line_edited and t._is_not_billed()):
            if timesheet.prevent_so_line_update:
                continue
            timesheet.so_line = timesheet.project_id.allow_billable and timesheet._timesheet_determine_sale_line()
