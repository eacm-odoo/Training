from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import datetime

from odoo import fields, models


class PlanningGenerateTimesheets(models.TransientModel):
    _name = 'planning.generate.timesheets'
    _description = "Generate Timesheets from Shifts"

    def _default_slot_ids(self):
        shifts = self.env['planning.slot'].browse(self._context.get('active_ids')) \
            .filtered(lambda s: s.resource_type == 'user' \
                                and s.state=='published' \
                                and s.employee_id.employee_type=='employee' \
                                and s.project_id \
                                and not (s.timesheets_generated and s.generated_timesheet_ids)
                    )
        return shifts

    slot_ids = fields.Many2many(
        string="Shifts",
        comodel_name='planning.slot',
        default=_default_slot_ids,
        domain="['|',('timesheets_generated','=',False),('generated_timesheet_ids','=',False), ('resource_type','=','user'), ('state','=','published'), ('employee_id.employee_type','=','employee'), ('project_id','!=', False)]",
    )
    start_date = fields.Date(string="Start Date", default=fields.Date.today().replace(day=1) - relativedelta(months=1))
    end_date = fields.Date(string="End Date", default=fields.Date.today().replace(day=1) - relativedelta(days=1))

    def action_confirm(self):
        self.ensure_one()
        selected_start_date = datetime.datetime.combine(self.start_date, datetime.time.min)
        selected_end_date = datetime.datetime.combine(self.start_date, datetime.time.max)
        start_datetime = timezone(self.env.user.tz or 'UTC').localize(selected_start_date).astimezone(utc).replace(tzinfo=None)
        end_datetime = timezone(self.env.user.tz or 'UTC').localize(selected_end_date + relativedelta(days=1)).astimezone(utc).replace(tzinfo=None)
        to_process, _ = self.slot_ids.filtered(lambda s: s.start_datetime < end_datetime and s.end_datetime > start_datetime and not (s.timesheets_generated and s.generated_timesheet_ids))._split_by_time(start_datetime, end_datetime)
        tz = timezone('UTC')
        for slot in to_process:
            calendar = slot.resource_id.calendar_id
            start_date = tz.localize(max(slot.start_datetime, start_datetime))
            end_date = tz.localize(min(slot.end_datetime, end_datetime))
            work_intervals = calendar._work_intervals_batch(start_date, end_date, resources=slot.resource_id)
            for _, work_interval in work_intervals.items():
                for interval in work_interval:
                    slot.create_timesheet(interval[0], interval[1])
            slot.timesheets_generated = True
        return True
