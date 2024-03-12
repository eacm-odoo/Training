from odoo import fields, models, api, _

class SignItemType(models.Model):
    _inherit = 'sign.item.type'

    dynamic_auto_field = fields.Boolean('Dynamic Auto-fill', default=False)

class SignItem(models.Model):
    _inherit = 'sign.item'

    name = fields.Char('Name', compute='_compute_name', store=False)

    def _compute_name(self): 
        for rec in self:
            if rec.type_id.dynamic_auto_field:
                rec.name = "Dipa"
            else:
                rec.name = rec.type_id.placeholder
