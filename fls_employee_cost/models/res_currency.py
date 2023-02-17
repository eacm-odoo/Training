from odoo import models, api
from datetime import date


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def get_conversion_rate(self, project_id):
        company = self.env['project.project'].browse([project_id]).company_id
        from_currency = company.currency_id
        to_currency = self.env['res.currency'].search([('name','=','USD')])
        currency_rates = (from_currency + to_currency)._get_rates(company, date.today().strftime("%m/%d/%y"))
        res = currency_rates.get(to_currency.id) / currency_rates.get(from_currency.id)
        return res