from odoo import api, fields, models
from datetime import date


class ProjectProductEmployeeMap(models.Model):
    _inherit = 'project.sale.line.employee.map'

    display_cost = fields.Monetary(currency_field='cost_currency_id', compute="_compute_display_cost", inverse="_inverse_display_cost", string="Hourly Cost")


    @api.depends('cost', 'employee_id.resource_calendar_id')
    def _compute_display_cost(self):
        is_uom_day = self.env.ref('uom.product_uom_day') == self.env.company.timesheet_encode_uom_id
        resource_calendar_per_hours = self._get_working_hours_per_calendar(is_uom_day)

        for map_line in self:
            if is_uom_day:
                map_line.display_cost = map_line.cost * resource_calendar_per_hours.get(map_line.employee_id.resource_calendar_id.id, 1)
            else:
                map_line.display_cost = map_line.cost
            try:
                currency_conversion_rate = self.env['res.currency']._get_conversion_rate(map_line.cost_currency_id,map_line.currency_id,map_line.company_id,date.today().strftime("%m/%d/%y"))
            except:
                currency_conversion_rate = 1
            map_line.display_cost *= currency_conversion_rate