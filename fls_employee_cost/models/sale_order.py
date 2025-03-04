from odoo import models, api, fields
from datetime import date

import logging
logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    invoiced_usd = fields.Float(string="Amount Invoiced USD", compute="_compute_untaxed_amount_invoiced", store=True)
    post_qty_invoiced = fields.Float(
        string="Invoiced Quantity (Posted Only)",
        compute='_compute_post_qty_invoiced',
        digits='Product Unit of Measure',
        store=True)

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _compute_post_qty_invoiced(self):
        """
        Copy of _compute_qty_invoiced() to exclude draft invoices from qty_invoiced. Computed for post_qty_invoiced()
        """
        for line in self:
            qty_invoiced = 0.0
            for invoice_line in line._get_invoice_lines():
                if invoice_line.move_id.state not in ['cancel', 'draft', 'to_approve', 'approved'] or invoice_line.move_id.payment_state == 'invoicing_legacy':
                    if invoice_line.move_id.move_type == 'out_invoice':
                        qty_invoiced += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
                    elif invoice_line.move_id.move_type == 'out_refund':
                        qty_invoiced -= invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
            line.post_qty_invoiced = qty_invoiced

    @api.depends('invoice_lines', 'invoice_lines.price_total', 'invoice_lines.move_id.state', 'invoice_lines.move_id.move_type')
    def _compute_untaxed_amount_invoiced(self):
        """ 
        Inherited to track the amount invoiced in USD in parallel to untaxed_amount_invoiced which could be in different currency
        """
        usd_currency = self.env['res.currency'].search([('name','=','USD')]) 
        for line in self:
            amount_invoiced = 0.0
            amount_invoiced_usd = 0.0
            for invoice_line in line._get_invoice_lines():
                if invoice_line.move_id.state == 'posted':
                    invoice_date = invoice_line.move_id.date or fields.Date.today()
                    if invoice_line.move_id.move_type == 'out_invoice':
                        amount_invoiced += invoice_line.currency_id._convert(invoice_line.price_subtotal, line.currency_id, line.company_id, invoice_date)
                        amount_invoiced_usd += invoice_line.currency_id._convert(invoice_line.price_subtotal, usd_currency, line.company_id, invoice_date)
                    elif invoice_line.move_id.move_type == 'out_refund':
                        amount_invoiced -= invoice_line.currency_id._convert(invoice_line.price_subtotal, line.currency_id, line.company_id, invoice_date)
                        amount_invoiced_usd -= invoice_line.currency_id._convert(invoice_line.price_subtotal, usd_currency, line.company_id, invoice_date)
            line.untaxed_amount_invoiced = amount_invoiced
            line.invoiced_usd = amount_invoiced_usd

    @api.depends('state', 'price_reduce', 'product_id', 'untaxed_amount_invoiced', 'qty_delivered', 'product_uom_qty')
    def _compute_untaxed_amount_to_invoice(self):
        """ Total of remaining amount to invoice on the sale order line (taxes excl.) as
                total_sol - amount already invoiced
            where Total_sol depends on the invoice policy of the product.

            Note: Draft invoice are ignored on purpose, the 'to invoice' amount should
            come only from the SO lines.
        """
        for line in self:
            amount_to_invoice = 0.0
            if line.state in ['sale', 'done']:
                # Note: do not use price_subtotal field as it returns zero when the ordered quantity is
                # zero. It causes problem for expense line (e.i.: ordered qty = 0, deli qty = 4,
                # price_unit = 20 ; subtotal is zero), but when you can invoice the line, you see an
                # amount and not zero. Since we compute untaxed amount, we can use directly the price
                # reduce (to include discount) without using `compute_all()` method on taxes.
                price_subtotal = 0.0
                uom_qty_to_consider = line.qty_delivered if line.product_id.invoice_policy == 'delivery' else line.product_uom_qty
                price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                price_subtotal = price_reduce * uom_qty_to_consider
                if len(line.tax_id.filtered(lambda tax: tax.price_include)) > 0:
                    # As included taxes are not excluded from the computed subtotal, `compute_all()` method
                    # has to be called to retrieve the subtotal without them.
                    # `price_reduce_taxexcl` cannot be used as it is computed from `price_subtotal` field. (see upper Note)
                    price_subtotal = line.tax_id.compute_all(
                        price_reduce,
                        currency=line.currency_id,
                        quantity=uom_qty_to_consider,
                        product=line.product_id,
                        partner=line.order_id.partner_shipping_id)['total_excluded']
                inv_lines = line._get_invoice_lines()
                # if any(inv_lines.mapped(lambda l: l.discount != line.discount)):
                #     # In case of re-invoicing with different discount we try to calculate manually the
                #     # remaining amount to invoice
                #     amount = 0
                #     for l in inv_lines:
                #         if len(l.tax_ids.filtered(lambda tax: tax.price_include)) > 0:
                #             amount += l.tax_ids.compute_all(l.currency_id._convert(l.price_unit, line.currency_id, line.company_id, l.date or fields.Date.today(), round=False) * l.quantity)['total_excluded']
                #         else:
                #             amount += l.currency_id._convert(l.price_unit, line.currency_id, line.company_id, l.date or fields.Date.today(), round=False) * l.quantity

                #     amount_to_invoice = max(price_subtotal - amount, 0)
                # else:
                    ##### CUSTOM CODE START #####
                qty_to_invoice = 0
                for aml in inv_lines.filtered(lambda l: l.parent_state in ['draft', 'to_approve', 'approved']):
                    currency_conversion_rate = self.env['res.currency']._get_conversion_rate(aml.currency_id,line.currency_id,aml.company_id,aml.move_id.date.strftime("%m/%d/%y"))
                    amount_to_invoice += aml.quantity * aml.price_unit * ((100-aml.discount)/100) * currency_conversion_rate
                    qty_to_invoice += aml.quantity
                if line.qty_delivered > line.qty_invoiced:
                    amount_to_invoice += (line.qty_delivered - line.qty_invoiced) * line.price_unit * ((100-line.discount)/100)
                    #####  CUSTOM CODE END  #####

            line.untaxed_amount_to_invoice = amount_to_invoice
