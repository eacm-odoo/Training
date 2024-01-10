from odoo import models,fields,api

class AccountMove(models.Model):
    _inherit = 'account.move'


    client_order_ref = fields.Char("Client Order Reference")
    reference = fields.Char("Reference")
    bank_acount_id = fields.Many2one(comodel_name='res.partner.bank')
    analytic_account_to_invoice = fields.Boolean(string= 'Analytic Account on Report?')
    currency_name = fields.Char(related = 'currency_id.name')
    
    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        for move in res:
            if move.sale_order_count>0:
                move.client_order_ref = move.line_ids.sale_line_ids[0].order_id.client_order_ref
                move.reference = move.line_ids.sale_line_ids[0].order_id.ref
        return res
