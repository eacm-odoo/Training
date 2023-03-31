from odoo import api, fields, models
from odoo.exceptions import AccessError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    freeze_timesheets = fields.Boolean(string="Freeze Timesheets", default=False, config_parameter='fls_timesheet_validation.freeze_timesheets')
    freeze_day = fields.Integer(string="Day of the month timesheets freeze", default=1, config_parameter='fls_timesheet_validation.freeze_day')

    @api.constrains('freeze_day')
    def _check_approval(self):
        for setting in self:
            if setting.freeze_day < 1 or setting.freeze_day > 28:
                raise AccessError("Day must be between 1 to 28!")
