from odoo import api, fields, models, _
from odoo.osv import expression
from datetime import timedelta

class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    timesheets_generated = fields.Boolean(string="Timesheets Generated", readonly=True, copy=False)
    timesheeted_hours = fields.Float(
        string="Timesheeted Hours",
        compute='_compute_timesheeted_hours',
        store=True,
        help="Number of hours on the employee's Timesheets for this shift"
    )
    generated_timesheet_ids = fields.One2many(
        string="Generated Timesheets", comodel_name='account.analytic.line', inverse_name='shift_id', readonly=True, copy=False
    )

    @api.depends('generated_timesheet_ids')
    def _compute_timesheeted_hours(self):
        for slot in self:
            slot.timesheeted_hours = sum(slot.generated_timesheet_ids.mapped('unit_amount'))
    
    def custom_action_generate_timesheets(self):
        return {
            'name': _("Generate Timesheets"),
            'res_model': 'planning.generate.timesheets',
            'view_mode': 'form',
            'context': {
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def _get_timesheet_domain(self):
        domain = super()._get_timesheet_domain()
        if domain:
            return expression.OR([expression.AND([domain, [('shift_id', '=', False)]]), [('shift_id', '=', self.id)]])
        else:
            return [('shift_id', '=', self.id)]

    def create_timesheet(self, start, end):
        timesheets = self.env['account.analytic.line']
        for slot in self:
            timesheets |= timesheets.create({
                'name': '/',
                'shift_id': slot.id,
                'project_id': slot.project_id.id,
                'task_id': slot.sale_line_id.task_id.id,
                'employee_id': slot.employee_id.id,
                'unit_amount': (end - start)/timedelta(hours=1) * slot.resource_id.time_efficiency / 100 * slot.allocated_percentage / 100,
                'date': start.date(),
            })
        return timesheets

    def _split_by_time(self, start, end):
        trimmed_slots = self.env['planning.slot']
        for slot in self:
            if slot.start_datetime < start < slot.end_datetime:
                trimmed_slots |= slot.copy({'start_datetime': slot.start_datetime, 'end_datetime': start, 'state': slot.state})
                slot.start_datetime = start
            if slot.start_datetime < end < slot.end_datetime:
                trimmed_slots |= slot.copy({'start_datetime': end, 'end_datetime': slot.end_datetime, 'state': slot.state})
                slot.end_datetime = end
        trimmed_slots._compute_allocated_hours()
        return (self, trimmed_slots)
