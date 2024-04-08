from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    bank_ids = fields.One2many(related='partner_id.bank_ids')
    bank_acount_id = fields.Many2one(
        comodel_name='res.partner.bank', 
        domain="[('id', 'in', bank_ids)]", 
        compute='_compute_partner_bank_id', readonly=False)
    partner_bank_id = fields.Many2one(
        'res.partner.bank',
        domain="[('id', 'in', bank_ids)]",
        string='Recipient Bank',
        compute='_compute_partner_bank_id', store=True, readonly=False,
        help="Bank Account Number to which the invoice will be paid. "
             "A Company bank account if this is a Customer Invoice or Vendor Credit Note, "
             "otherwise a Partner bank account number.",
        check_company=True,
        tracking=True,
    )

    @api.depends('bank_ids')
    def _compute_partner_bank_id(self):
        for move in self:
            if move.bank_ids:
                move.bank_acount_id = move.bank_ids[0]
                move.partner_bank_id = move.bank_ids[0]

