from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class SignItemType(models.Model):
    _inherit = 'sign.item.type'

    dynamic_auto_field = fields.Boolean('Dynamic Auto-fill', default=False)

    @api.constrains('auto_field')
    def _check_auto_field_exists(self):
        partner = self.env['res.partner'].browse(self.env.user.partner_id.id)
        for sign_type in self:
            if sign_type.auto_field:
                try:
                    if sign_type.dynamic_auto_field:
                        employee = self.env.user.employee_id
                        continue
                        if isinstance(employee.mapped(sign_type.auto_field), models.BaseModel):
                            raise AttributeError
                    elif isinstance(partner.mapped(sign_type.auto_field), models.BaseModel):
                        raise AttributeError

                except (KeyError, AttributeError):
                    raise ValidationError(_("Malformed expression: %(exp)s", exp=sign_type.auto_field))

# class SignItem(models.Model):
#     _inherit = 'sign.item'

#     name = fields.Char('Name', compute='_compute_name', store=False)

#     def _compute_name(self): 
#         for rec in self:
#             if rec.type_id.dynamic_auto_field:
#                 rec.name = "Dipa"
#             else:
#                 rec.name = rec.type_id.placeholder
