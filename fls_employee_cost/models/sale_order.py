from odoo import models, api, fields
from datetime import date


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    invoiced_usd = fields.Float(string="Amount Invoiced USD", compute="_compute_untaxed_amount_invoiced", store=True)

    @api.depends('invoice_lines', 'invoice_lines.price_total', 'invoice_lines.move_id.state', 'invoice_lines.move_id.move_type')
    def _compute_untaxed_amount_invoiced(self):
        """ Compute the untaxed amount already invoiced from the sale order line, taking the refund attached
            the so line into account. This amount is computed as
                SUM(inv_line.price_subtotal) - SUM(ref_line.price_subtotal)
            where
                `inv_line` is a customer invoice line linked to the SO line
                `ref_line` is a customer credit note (refund) line linked to the SO line
        """
        usd_currency = self.env['res.currency'].search([('name','=','USD')]) 
        for line in self:
            amount_invoiced = 0.0
            amount_invoiced_usd = 0.0
            for invoice_line in line._get_invoice_lines():
                if invoice_line.move_id.state == 'posted':
                    invoice_date = invoice_line.move_id.invoice_date or fields.Date.today()
                    if invoice_line.move_id.move_type == 'out_invoice':
                        amount_invoiced += invoice_line.currency_id._convert(invoice_line.price_subtotal, line.currency_id, line.company_id, invoice_date)
                        amount_invoiced_usd += invoice_line.currency_id._convert(invoice_line.price_subtotal, usd_currency, line.company_id, invoice_date)
                    elif invoice_line.move_id.move_type == 'out_refund':
                        amount_invoiced -= invoice_line.currency_id._convert(invoice_line.price_subtotal, line.currency_id, line.company_id, invoice_date)
                        amount_invoiced_usd -= invoice_line.currency_id._convert(invoice_line.price_subtotal, usd_currency, line.company_id, invoice_date)
            line.untaxed_amount_invoiced = amount_invoiced
            line.invoiced_usd = amount_invoiced_usd
