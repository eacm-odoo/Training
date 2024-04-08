from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    employee_id = fields.Many2one('hr.employee', string='FLS Employee', compute='_compute_employee_id', store=True)

    @api.depends('employee_ids')
    def _compute_employee_id(self):
        for partner in self:
            partner.employee_id = partner.employee_ids[0] if partner.employee_ids else False
