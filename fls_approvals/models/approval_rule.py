from odoo import models, fields

class ApprovalRule(models.Model):
    _name = 'approval.rule'
    _description = 'Approval Rule'

    name = fields.Char(string='Name', required=True)
    amount = fields.Float(string='Amount')
    company_id = fields.Many2one('res.company', string='Company')
    department_id = fields.Many2one('hr.department', string='Department')
    user_id = fields.Many2one('res.users', string='User')
    models = fields.Selection([
        ('sale.order', 'Sale Order'),
        ('purchase.order', 'Purchase Order'),
        ('account.move', 'Journal Entry')
    ], string='Models')
    type = fields.Selection([
        ('vendor.bill','Vendor Bill'),
        ('journal.entry','Journal Entry'),
        ('sale.invoice','Customer Invoice')])
    project_manager = fields.Boolean(string='Project Manager')
    delivery_director = fields.Boolean(string='Delivery Director')
    salesperson = fields.Boolean(string='Salesperson')
    buyer = fields.Boolean(string='Buyer')
    timesheet_approver = fields.Boolean(string='Timesheet Approver')
    sequence = fields.Integer(string='Sequence')
