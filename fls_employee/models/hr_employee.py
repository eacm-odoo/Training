from odoo import models, api, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model_create_multi
    def create(self, vals_list):
        for record in vals_list:
            if self.search([('name', 'ilike', record.get('name'))]): raise UserError(_('An employee with a similar name already exists.'))
        return super(HrEmployee, self).create(vals_list)
    
    