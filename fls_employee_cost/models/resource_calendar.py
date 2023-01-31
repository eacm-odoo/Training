from odoo import fields, models, api


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    week_hours = fields.Float(string='Hours in a week', compute="_compute_week_hours")

    @api.depends('attendance_ids','attendance_ids.hour_to', 'attendance_ids.hour_from')
    def _compute_week_hours(self):
        for calendar in self:
            calendar.week_hours = 0
            for line in calendar.attendance_ids:
                calendar.week_hours += line.hour_to - line.hour_from