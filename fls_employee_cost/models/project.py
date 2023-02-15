from odoo import fields, models, api


class Project(models.Model):
    _inherit = 'project.project'

    sale_order_id = fields.Many2one(string='Sales Order', related='sale_line_id.order_id', help="Sales order to which the project is linked.", store=True)
    billed_cost = fields.Float(string="Billed Cost", compute='_compute_profitability', store=True)
    invoiced_revenue = fields.Float(string="Invoiced Revenue", compute='_compute_profitability', store=True)
    current_margin = fields.Float(string="Current Margin", compute='_compute_profitability', store=True)
    current_margin_percentage = fields.Float(string="Current Margin %", compute='_compute_profitability', store=True, group_operator="avg")
    to_bill_cost = fields.Float(string="To Bill Cost", compute='_compute_profitability', store=True)
    to_invoice_revenue = fields.Float(string="To Invoice Revenue", compute='_compute_profitability', store=True)
    future_margin = fields.Float(string="Future Margin", compute='_compute_profitability', store=True)
    future_margin_percentage = fields.Float(string="Future Margin %", compute='_compute_profitability', store=True, group_operator="avg")
    expected_cost = fields.Float(string="Expected Cost", compute='_compute_profitability', store=True)
    expected_revenue = fields.Float(string="Expected Revenue", compute='_compute_profitability', store=True)
    expected_margin = fields.Float(string="Expected Margin", compute='_compute_profitability', store=True)
    expected_margin_percentage = fields.Float(string="Expected Margin %", compute='_compute_profitability', store=True, group_operator="avg")

    def _compute_profitability(self):
        for project in self:
            items = project._get_profitability_items()
            usd_conversion_rate = self.env['res.currency'].get_conversion_rate(project.id)
            project.invoiced_revenue = items['revenues']['total']['invoiced']*usd_conversion_rate
            project.billed_cost = items['costs']['total']['billed']*usd_conversion_rate
            project.current_margin = project.invoiced_revenue + project.billed_cost
            project.current_margin_percentage = project.current_margin / project.invoiced_revenue if project.invoiced_revenue != 0 else 0
            project.to_invoice_revenue = items['revenues']['total']['to_invoice']*usd_conversion_rate
            project.to_bill_cost = items['costs']['total']['to_bill']*usd_conversion_rate
            project.future_margin = project.to_invoice_revenue + project.to_bill_cost
            project.future_margin_percentage = project.future_margin / project.to_invoice_revenue if project.to_invoice_revenue != 0 else 0
            project.expected_revenue = project.invoiced_revenue + project.to_invoice_revenue
            project.expected_cost = project.billed_cost + project.to_bill_cost
            project.expected_margin = project.current_margin + project.future_margin
            project.expected_margin_percentage = project.expected_margin / project.expected_revenue if project.expected_revenue != 0 else 0
