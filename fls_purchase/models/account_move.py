from odoo import models, fields, api
from datetime import datetime


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        for line in self.line_ids.mapped('purchase_line_id'):
            purchase_id = line.order_id
            date_planned = purchase_id.date_planned.date()
            if self.move_type == "in_invoice" and purchase_id and date_planned:
                    vals['date'] = date_planned
        res = super(AccountMove, self).write(vals)
        return res
