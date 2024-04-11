from odoo import fields, models


class AccountMoveSelectTemplate(models.TransientModel):
    _name = "account.move.select.template"
    _description = "Select Invoice Template"

    pdf_report_id = fields.Many2one("ir.actions.report", string="PDF Template", domain=[("model", "=", "account.move")])
