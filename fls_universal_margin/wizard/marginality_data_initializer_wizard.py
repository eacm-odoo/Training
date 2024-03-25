from odoo import models, fields


class MarginalityDataInitializer(models.TransientModel):
    _name = 'marginality.data.initializer.wizard'
    _description = 'Marginality Data Initializer Wizard'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)

    def button_confirm(self):
        self.ensure_one()
        self.env['marginality.data'].initialize_data(self.date_from, self.date_to)
        return {'type': 'ir.actions.act_window_close'}

    def button_cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    
