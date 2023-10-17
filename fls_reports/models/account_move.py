from odoo import models,fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    client_order_ref = fields.Char(compute = 'compute_sale_order_id')
    bank_acount_id = fields.Many2one(comodel_name='res.partner.bank')
    analytic_account_to_invoice = fields.Boolean(string="Analytic Account on Report?")
    def compute_sale_order_id(self):
        if self.sale_order_count>0:
            self.client_order_ref = self.line_ids.sale_line_ids.order_id.client_order_ref
        else:
            self.client_order_ref = ""
