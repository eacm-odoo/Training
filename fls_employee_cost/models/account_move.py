from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _update_currency_lines(self):
        USD = self.env['res.currency'].search([('name','=','USD')])
        for line in self.line_ids.filtered(lambda l: l.product_id.invoice_policy in ['delivered_manual', 'delivered_milestones']):
            line.credit = line.currency_id._convert(line.credit, USD, line.company_id, line.date)

    def update_currencies(self):
        self._update_currency_lines()

    @api.model
    def action_update_currencies(self):
        for move in self:
            move._update_currency_lines()
