from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    date = fields.Date(compute="_compute_accounting_date", store=True)

    @api.depends("purchase_id.date_planned", "purchase_id")
    def _compute_accounting_date(self):
        for mv in self:
            if mv.move_type == "in_invoice" and mv.date and mv.purchase_id.date_planned:
                mv.date = mv.purchase_id.date_planned.date()
