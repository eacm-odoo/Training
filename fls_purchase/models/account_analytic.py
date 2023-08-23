from odoo import models, fields, api


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    recent_contract_id = fields.Many2one("hr.contract", compute="_compute_contract_id", store="True")

    @api.depends("employee_id", "employee_id.contract_ids")
    def _compute_contract_id(self):
        for line in self:
            for contract in line.employee_id.contract_ids:
                if contract.state == "open" and line.recent_contract_id != False and contract.id > line.recent_contract_id.id:
                    line.recent_contract_id = contract.id
