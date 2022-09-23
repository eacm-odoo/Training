import datetime
from collections import OrderedDict, defaultdict
from datetime import date, datetime, timedelta
from pytz import timezone

from odoo import api, fields, models
from odoo.tools.misc import get_lang


class ResourceBenchReport(models.Model):
    _name = 'hr.bench.report'
    _description = "Bench Report"
    _auto = False

    # Primary identifier fields
    id = fields.Integer(string="ID", readonly=True)
    name = fields.Char(related='employee_id.name', readonly=True)
    date = fields.Date(string="Date", readonly=True)
    employee_id = fields.Many2one(string="Employee", comodel_name='hr.employee', readonly=True)

    # Pseudo-compute fields.
    # These are computed fields but since we need to be able to aggregate them, they have to be stored
    # in the database. Unfortunately, SQL views require all stored fields to be selected in the sql query.
    # This leads to an issue since once it's read from the database, the compute fields won't run. So,
    # to get around this, we precompute the values and then select them directly in the sql query.
    available_hours = fields.Float(string="Available Hours", readonly=True)
    planned_hours = fields.Float(string="Planned Hours", readonly=True)
    timesheeted_hours = fields.Float(string="Timesheeted Hours", readonly=True)
    wasted_hours = fields.Float(string="Wasted Hours", readonly=True)
    occupied_percent = fields.Float(string="Occupied %", group_operator='avg', readonly=True)

    @property
    def _table_query(self):
        today = fields.Date.today()
        lang = get_lang(self.env)
        date_start = self._context.get('date_start', today - timedelta(days=(today.weekday() + 1 - int(lang.week_start)) % 7))
        if not isinstance(date_start, date):
            date_start = fields.Date.from_string(date_start)
        date_end = self._context.get('date_end', date_start + timedelta(weeks=4, days=-1))
        if not isinstance(date_end, date):
            date_end = fields.Date.from_string(date_end)

        employees = self.env['hr.employee'].search([])
        computed_hours = self._calculate_employee_hours(date_start, date_end, employees)

        values = [f"({v['employee_id']}, '{v['date']}'::date, {v['available_hours']}, {v['planned_hours']})" for v in computed_hours]
        hours_fields = list(computed_hours[0].keys())

        return """
            SELECT 
                *,
                CASE WHEN t.available_hours=0 THEN 0 ELSE 1.0-(t.wasted_hours/t.available_hours) END as occupied_percent
            FROM 
            (
                SELECT
                    hr_employee.id as employee_id,
                    date_series.date as date,
                    ROW_NUMBER () OVER (ORDER BY hr_employee.id, date_series.date) as id,
                    coalesce(work_times.available_hours,0) as available_hours,
                    coalesce(work_times.planned_hours,0) as planned_hours,
                    coalesce(timesheets.hours,0) as timesheeted_hours,
                    CASE WHEN coalesce(work_times.available_hours,0)=0 THEN 0
                        WHEN coalesce(timesheets.hours, 0)=0 THEN work_times.available_hours-work_times.planned_hours
                        ELSE work_times.available_hours-timesheets.hours
                    END as wasted_hours
                FROM hr_employee
                CROSS JOIN (SELECT generate_series('%(date_start)s'::timestamp, '%(date_end)s'::timestamp, '1 day')::date date) as date_series
                LEFT JOIN (
                    SELECT
                        employee_id,
                        date_trunc('minute', date) as date,
                        sum(unit_amount) as hours
                    FROM account_analytic_line
                    WHERE date >= '%(date_start)s'::timestamp AND date <= '%(date_end)s'::timestamp
                    GROUP BY employee_id, date
                ) as timesheets ON timesheets.employee_id = hr_employee.id AND timesheets.date = date_series.date
                LEFT OUTER JOIN (
                    SELECT * FROM (VALUES %(values)s) as t (%(fields)s)
                ) as work_times on work_times.employee_id = hr_employee.id AND work_times.date = date_series.date
            ) as t
            WHERE t.available_hours > 0
        """ % {
            'date_start': date_start,
            'date_end': date_end,
            'values': ', '.join(values),
            'employee_ids': tuple(employees.ids),
            'fields': ', '.join(hours_fields),
        }

    def _calculate_employee_hours(self, date_start, date_end, employees):
        values = []
        for employee in employees:
            calendar = employee.resource_id.calendar_id
            tz = timezone(calendar.tz)
            employee_date_start = tz.localize(datetime.combine(date_start, datetime.min.time()))
            employee_date_end = tz.localize(datetime.combine(date_end, datetime.min.time()))
            day_totals = calendar._get_resources_work_day_total(employee_date_start, employee_date_end, employee.resource_id)

            planned_total = defaultdict(lambda: defaultdict(float))
            employee_slots = self.env['planning.slot'].search([('state', '=', 'published'), ('employee_id', '=', employee.id), '!', '|',
                                                               ('start_datetime', '>=', employee_date_end),
                                                               ('end_datetime', '<=', employee_date_start), ('project_id', '!=', False)])
            for slot in employee_slots:
                slot_start = max(tz.localize(slot.start_datetime), employee_date_start)
                slot_end = min(tz.localize(slot.end_datetime), employee_date_end)
                work_intervals = calendar._work_intervals_batch(slot_start, slot_end, resources=slot.resource_id)
                for start, stop, meta in work_intervals[slot.resource_id.id]:
                    planned_total[slot.resource_id.id][start.date()] += (stop - start).total_seconds() / 3600 * slot.allocated_percentage / 100

            values.extend([{
                'employee_id': employee.id,
                'date': date,
                'available_hours': available_hours,
                'planned_hours': planned_total[employee.resource_id.id][d]
            } for date, available_hours in day_totals[employee.resource_id.id].items()])
        return values

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'occupied_percent' in fields:
            fields.extend([
                'aggregated_available_hours:array_agg(available_hours)',
                'aggregated_wasted_hours:array_agg(wasted_hours)',
            ])
        res = super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for data in res:
            if 'occupied_percent' in data:
                total_available_hours = float(sum(data['aggregated_available_hours']))
                total_wasted_hours = float(sum(data['aggregated_wasted_hours']))
                data.update(occupied_percent=total_available_hours and 1.0 - (total_wasted_hours / total_available_hours) or 0)
        return res
