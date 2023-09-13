from odoo import models, fields, api
from datetime import datetime


class AccountMove(models.Model):
    _inherit = "account.move"

    date = fields.Date(compute="_compute_accounting_date", store=True)

    @api.depends("line_ids")
    def _compute_accounting_date(self):
        for mv in self:
            mv.date = datetime.today()
            for line in mv.line_ids.mapped('purchase_line_id'):
                purchase_id = line.order_id
                date_planned = purchase_id.date_planned.date()
                if mv.move_type == "in_invoice" and purchase_id and date_planned:
                    mv.date = date_planned

