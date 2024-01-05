from odoo import api, fields, models, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    cost_usd = fields.Float(string="Cost USD", compute='_compute_cost_usd', store=True)

    @api.depends('amount', 'currency_id')
    def _compute_cost_usd(self):
        usd_currency = self.env['res.currency'].search([('name','=','USD')], limit=1) 
        for line in self:
            line.cost_usd = 0
            if line.currency_id and line.company_id and line.date:
                currency_conversion_rate = self.env['res.currency']._get_conversion_rate(line.currency_id,usd_currency,line.company_id,line.date.strftime("%m/%d/%y"))
                line.cost_usd = line.amount * currency_conversion_rate

    def _compute_line_revenue_usd(self, rec_month=None, rec_year=None, rec_employee_id=None):
        if self:
            rec_month = self.date.month
            rec_year = self.date.year
            rec_employee_id = self.employee_id.id
        usd_currency = self.env['res.currency'].search([('name','=','USD')], limit=1)
        revenue = 0
        if not rec_month or not rec_year or not rec_employee_id:
            return 0

        sol = self.so_line
        if len(sol) != 1 and sol.product_id.service_policy != 'delivered_timesheet':
            return 0
        # Computes Revenue
        filtered_invoice_lines = sol.invoice_lines.filtered(
            lambda aml: aml.move_id.date.month == rec_month and aml.move_id.date.year == rec_year
        )

        for aml in filtered_invoice_lines:
            # if aml.currency_id != usd_currency:
                # currency_conversion_rate = self.env['res.currency']._get_conversion_rate(aml.currency_id,usd_currency,aml.company_id,aml.move_id.date.strftime("%m/%d/%y"))
            revenue += aml.price_subtotal * aml.conversion_rate
        
        filtered_timesheet_ids = sol.timesheet_ids.filtered(
            lambda aal: aal.date.month == rec_month and aal.date.year == rec_year)

        employee_timesheet_counter = len([aal for aal in filtered_timesheet_ids if aal.employee_id.id == rec_employee_id])
        revenue /= len(filtered_timesheet_ids.employee_id.ids) or 1
        revenue /= employee_timesheet_counter or 1
        return revenue
