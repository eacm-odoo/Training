from odoo import models, fields,api
from odoo.exceptions import ValidationError

class ApprovalRule(models.Model):
    _name = 'approval.rule'
    _description = 'Approval Rule'
    _order = 'sequence'


    name = fields.Char(string='Name', required=True)
    amount = fields.Float(string='Amount')
    company_id = fields.Many2one('res.company', string='Company')
    department_id = fields.Many2one('hr.department', string='Department')
    user_id = fields.Many2one('res.users', string='User')
    models = fields.Selection([
        ('sale.order', 'Sale Order'),
        ('purchase.order', 'Purchase Order'),
        ('account.move', 'Journal Entry')
    ], string='Models',required=True,default='sale.order')
    type = fields.Selection([
        ('vendor.bill','Vendor Bill'),
        ('journal.entry','Journal Entry'),
        ('sale.invoice','Customer Invoice')])
    project_manager = fields.Boolean(string='Project Manager')
    delivery_director = fields.Boolean(string='Delivery Director')
    salesperson = fields.Boolean(string='Salesperson')
    buyer = fields.Boolean(string='Buyer')
    timesheet_approver = fields.Boolean(string='Timesheet Approver')
    sequence_toggle = fields.Integer(string='Toggle')
    sequence = fields.Integer(string='Sequence',related='sequence_toggle')
    domain = fields.Char(string='Domain',default='[]')
    currency_string = fields.Char(string = 'Currency is in',compute = "_compute_currency")

    @api.constrains('project_manager', 'delivery_director', 'salesperson', 'buyer', 'timesheet_approver','user_id')
    def _check_approval_roles(self):
        for record in self:
            if not any([record.project_manager, record.delivery_director, record.salesperson, record.buyer, record.timesheet_approver,record.user_id]):
                raise ValidationError("At least one approval role must be selected.")
    
    @api.onchange('models')
    def onchange_models(self):
        if self.models != 'account.move':
            self.type = False
    
    @api.onchange('company_id')
    def _compute_currency(self):
        self.currency_string = "USD" if not self.company_id else self.company_id.currency_id.name
    
    @api.model_create_multi
    def create(self,vals_list):
        res = super().create(vals_list)
        res.sequence_toggle = self.env['ir.sequence'].next_by_code('approval.sequence.value')
        return res
    
    amount_fields = set(['amount_untaxed','amount_total'])

    def convert_currency_in_domain_filter(self,domain,currency_conversion_rate):
        for i in range(len(domain)):
            condition = domain[i]
            if condition[0] in self.amount_fields:
                condition_list = list(condition)
                condition_list[2] = condition_list[2]*currency_conversion_rate
                condition = tuple(condition_list)
            domain[i] = condition
        return domain
