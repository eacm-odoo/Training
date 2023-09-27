from odoo import fields, models, Command, api, _ 
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    approver_ids = fields.Many2many('res.users', string = 'Approvers')
    state = fields.Selection(selection_add = [
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('sale','Sales Order')
    ])
    current_approver = fields.Many2one('res.users',string = 'Current Approver')
    current_approver_id = fields.Integer('Current Approver Id', compute = '_compute_approver_id')
    loggedin_user_id = fields.Integer('Loggedin User', compute = '_compute_current_loggedin_user')
    
    def action_send_validate_so_email(self):
        self.state = 'to_approve'

        approval_rules = sorted(self.env['approval.rule'].search([('models','=','sale.order')]),key = lambda x :x.sequence)
        for rule in approval_rules:
            if rule.project_manager and self.amount_total > rule.amount and self.company_id == rule.company_id: #Add Department
                project = self.env['project.project'].search([('sale_line_id.order_id.id','=',self.id)])
                if project:
                    self.approver_ids = [Command.link(project.user_id.id)]

            if self.company_id == rule.company_id and self.amount_total > rule.amount and rule.user_id:
                self.approver_ids = [Command.link(rule.user_id.id)]
            if rule.delivery_director and self.amount_total > rule.amount and self.company_id == rule.company_id: #Add Department
                self.approver_ids = [Command.link(self.x_studio_delivery_director.id)]
            if rule.salesperson and self.amount_total > rule.amount and self.company_id == rule.company_id: #Add Department
                self.approver_ids = [Command.link(self.user_id.id)]
        if self.approver_ids:
            self.current_approver = self.approver_ids.ids[0]
            self.env['mail.template'].sudo().browse([self.env.ref('fls_approvals.email_template_validate_so').id]).send_mail(self.id, force_send=True)
        else:
            self.state = 'approved'
    
    def action_approve(self):
        if self.current_approver_id!= self.loggedin_user_id:
            raise UserError(_('Unable to Approver Record, This record has to be approved by ' + self.current_approver.name))
        approvers = self.approver_ids.ids
        message = self.current_approver.email_formatted+ 'has approved this Sale Order'
        self.message_post(body=message)
        current_approver_index = approvers.index(self.current_approver.id)
        if len(approvers) == current_approver_index+1:
            self.current_approver = None
            self.state = 'approved'
        else:
            self.current_approver = approvers[current_approver_index+1]
            self.env['mail.template'].sudo().browse([self.env.ref('fls_approvals.email_template_validate_so').id]).send_mail(self.id, force_send=True)

    @api.depends('current_approver')
    def _compute_approver_id(self):
        for record in self:
            record.current_approver_id = record.current_approver.id

    def _compute_current_loggedin_user(self):
        for record in self:
            record.loggedin_user_id = self.env.context.get('uid', 0)
