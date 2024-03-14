from odoo import models,fields,api


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_tag_ids = fields.Many2many(string="Tags",name='Tags',comodel_name='crm.tag')


    @api.model_create_multi
    def create(self, vals):
        moves = super().create(vals)
        sale_order_tags = {}
        for move in moves:
            tags = set()
            for line in move.invoice_line_ids.filtered('sale_line_ids'):
                for tag in line.sale_line_ids.mapped('order_id.tag_ids'):
                    tags.add(tag.id)
            sale_order_tags[move.id] = list(tags)
        for move in moves:
            move.sale_order_tag_ids = sale_order_tags[move.id]
        return moves


