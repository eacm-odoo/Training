from odoo import models, api, fields


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def update_currencies(self):
        USD = self.env['res.currency'].search([('name','=','USD')])
        for line in self.line_ids.filtered(lambda l: l.product_id.invoice_policy in ['delivery', 'delivered_manual']):
            line.credit = line.currency_id._convert(line.credit, USD, line.company_id, line.date)

