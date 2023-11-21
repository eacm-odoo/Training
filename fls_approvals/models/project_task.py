from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    sale_line_id = fields.Many2one(
        'sale.order.line',
        domain="""[
            ('company_id', '=', company_id),
            '|', '|', ('order_partner_id', 'child_of', partner_id if partner_id else []), ('order_id.partner_shipping_id', 'child_of', partner_id if partner_id else []),
            '|', ('order_partner_id', '=?', partner_id), ('order_id.partner_shipping_id', '=?', partner_id),
            ('is_service', '=', True), ('is_expense', '=', False)
        ]"""
    )
