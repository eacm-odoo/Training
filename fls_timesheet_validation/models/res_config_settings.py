from datetime import date

from odoo import api, fields, models
from odoo.exceptions import AccessError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    freeze_timesheets = fields.Boolean(string="Freeze Timesheets", default=False, config_parameter='fls_timesheet_validation.freeze_timesheets')
    freeze_day = fields.Integer(string="Day of the month of timesheets freeze", config_parameter='fls_timesheet_validation.freeze_day')
    freeze_month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'),('4', 'April'), ('5', 'May'), ('6', 'June'),('7', 'July'), ('8', 'August'), ('9', 'September'),('10', 'October'), ('11', 'November'), ('12', 'December')], string="Month of the timesheets freeze", config_parameter='fls_timesheet_validation.freeze_month')
    freeze_year = fields.Char(string="Year of the timesheets freeze", config_parameter='fls_timesheet_validation.freeze_year')

    @api.constrains('freeze_day', 'freeze_month', 'freeze_year')
    def _check_approval(self):
        for setting in self:
            try:
                date_obj = date(int(setting.freeze_year), int(setting.freeze_month), setting.freeze_day)
            except:
                raise AccessError("{}/{}/{} is not a real date!".format(setting.freeze_month,setting.freeze_day,setting.freeze_year))
