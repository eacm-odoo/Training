from odoo import models, fields, api, _

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'


    @api.model
    def open_analytic_line_split(self):
        return {
            'name': _('Split Timesheets'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.analytic.line.split',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
