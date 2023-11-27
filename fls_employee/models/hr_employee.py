from odoo import fields, models, api, _
from odoo.exceptions import UserError

import re


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _normalize_name(self, name):
        return re.sub(' +', ' ', name).strip() if name else name

    @api.model_create_multi
    def create(self, vals_list):
        for record in vals_list:
            name = record.get('name')
            normalized_name = self._normalize_name(name)
            domain = ['|', ('name', '=ilike', normalized_name), ('name', 'ilike', name)]
            if self.search(domain, limit=1):
                raise UserError(_('An employee with a similar name already exists.'))
                
        return super(HrEmployee, self).create(vals_list)
