from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    freeze_timesheets = fields.Boolean(string="Freeze Timesheets", config_parameter='fls_timesheet_validation.freeze_timesheets')
    freeze_day = fields.Integer(string="Day of the month timesheets freeze", default=1, config_parameter='fls_timesheet_validation.freeze_day')