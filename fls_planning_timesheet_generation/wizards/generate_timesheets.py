from dateutil.relativedelta import relativedelta
from pytz import timezone

from odoo import fields, models


class PlanningGenerateTimesheets(models.TransientModel):
    _name = 'planning.generate.timesheets'
    _description = "Generate Timesheets from Shifts"

    def _default_slot_ids(self):
        shifts = self.env['planning.slot'].browse(self._context.get('active_ids')) \
            .filtered(lambda s: s.resource_type == 'user' \
                                and s.state=='published' \
                                and s.employee_id.employee_type=='employee' \
                                and s.project_id and not s.timesheets_generated
                    )
        return shifts

    slot_ids = fields.Many2many(
        string="Shifts",
        comodel_name='planning.slot',
        default=_default_slot_ids,
        domain="[('timesheets_generated','=',False), ('resource_type','=','user'), ('state','=','published'), ('employee_id.employee_type','=','employee'), ('start_datetime', '<', end_date), ('end_datetime', '>', startdate), ('project_id','!=', False)]",
    )
    start_date = fields.Datetime(string="Start Date", default=fields.Datetime.now().replace(day=1))
    end_date = fields.Datetime(string="End Date", default=fields.Datetime.now() + relativedelta(day=31))

    def action_confirm(self):
        self.ensure_one()
        to_process, _ = self.slot_ids.filtered(lambda s: s.start_datetime < self.end_date and s.end_datetime > self.start_date and not s.timesheets_generated)._split_by_time(self.start_date, self.end_date)
        timesheets = self.env['account.analytic.line']
        for slot in to_process:
            calendar = slot.resource_id.calendar_id
            tz = timezone(calendar.tz)
            start_date = tz.localize(max(slot.start_datetime, self.start_date))
            end_date = tz.localize(min(slot.end_datetime, self.end_date))
            work_intervals = calendar._work_intervals_batch(start_date, end_date, resources=slot.resource_id)
            for _, work_interval in work_intervals.items():
                for interval in work_interval:
                    slot.create_timesheet(interval[0], interval[1])
            slot.timesheets_generated = True
        return True
