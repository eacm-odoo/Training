from odoo import models, fields

class AnalyticAccountHistory(models.Model):
    _name = 'analytic.account.history'
    _description = 'Analytic Account History'

    date = fields.Date(string='Date')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    project_manager_id  = fields.Many2one('res.users', string='Project Manager')
    operating_director_id = fields.Many2one('res.users', string='Operating Director')
    salesperson_id = fields.Many2one('res.users', string='Salesperson')
    project_name = fields.Char(string='Project Name')
    
