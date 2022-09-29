from odoo import fields, models, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    shift_id = fields.Many2one(string="Shift", comodel_name='planning.slot', copy=False, readonly=True)
    time_type = fields.Selection(string="Type", selection=[('regular', 'Regular'), ('overtime', 'Overtime')], default='regular')
    is_adjusted = fields.Boolean(string="Adjusted", default=False, copy=False)

    is_generated = fields.Boolean(string="Generated", compute="_compute_is_generated")

    def _compute_is_generated(self):
        for timesheet in self:
            timesheet.is_generated = bool(timesheet.shift_id)
