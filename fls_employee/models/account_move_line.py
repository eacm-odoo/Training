from odoo import api, fields, models, _

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    conversion_rate = fields.Float(string="Conversion Rate", compute='_compute_conversion_rate', default=1.0, store=True)

    @api.depends('currency_id','company_id','date', 'move_id')
    def _compute_conversion_rate(self):
        usd_id = self.env['res.currency'].search([('name','=','USD')], limit=1)
        conversion_rates = {}

        for line in self:
            # Set a default conversion rate
            line.conversion_rate = 1

            if line.currency_id and line.company_id and line.date:
                key = (line.date.strftime("%m/%d/%y"), line.currency_id.id)
                if key not in conversion_rates:
                    # Perform the query to get the conversion rate
                    currency_conversion_rate = self.env['res.currency']._get_conversion_rate(
                        line.currency_id, usd_id, line.company_id, line.date.strftime("%m/%d/%y"))
                    conversion_rates[key] = currency_conversion_rate

                line.conversion_rate = conversion_rates[key]
