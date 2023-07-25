from odoo import models, api, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('balance', 'move_id.is_storno')
    def _compute_debit_credit(self):
        super(AccountMoveLine, self)._compute_debit_credit()

        USD = self.env['res.currency'].search([('name','=','USD')])

        for line in self.filtered(lambda l: l.currency_id != USD):
            line.credit = line.currency_id._convert(line.credit, USD, line.company_id, line.date)

