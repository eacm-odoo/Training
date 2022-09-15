from odoo import fields, models, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    shift_id = fields.Many2one(comodel_name='planning.slot', string="Shift", copy=False)
    time_type = fields.Selection(string="Type", selection=[('regular', 'Regular'), ('overtime', 'Overtime')], default='regular')
    is_adjusted = fields.Boolean(string="Adjusted", default=False, copy=False)
