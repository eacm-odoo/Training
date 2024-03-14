from odoo import fields, models, Command, api, _ , SUPERUSER_ID
from odoo.exceptions import UserError
import ast

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    approver_ids = fields.Many2many('res.users', string = 'Approvers')
    state = fields.Selection(selection_add = [
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('sale','Sales Order'),
        ('rejected', 'Rejected')
    ])
    current_approver = fields.Many2one('res.users',string = 'Current Approver')
    current_approver_id = fields.Integer('Current Approver Id', compute = '_compute_approver_id')
    loggedin_user_id = fields.Integer('Loggedin User', compute = '_compute_current_loggedin_user')
    department_id = fields.Many2one('hr.department', string='Department')
    no_of_approvals = fields.Integer('No of Approvals')
    bookkeeper_id = fields.Many2one('res.users',string='Bookkeeper',required = True)

    def _send_approval_reminder_mail(self,template_name):
        template = self.env.ref(template_name, raise_if_not_found=False)
        if template:
            self.with_user(SUPERUSER_ID).with_context(is_reminder=True).message_post_with_template(template.id, email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature", composition_mode='comment')

    def action_send_validate_so_email(self):

        approval_rules = sorted(self.env['approval.rule'].search([('models','=','sale.order')]),key = lambda x :x.sequence)
        for rule in approval_rules:
            currency_conversion_rate = self.env['res.currency']._get_conversion_rate(rule.company_id.currency_id if rule.company_id else self.env['res.currency'].search([('name','=','USD')], limit=1),self.currency_id,self.company_id,self.date_order.strftime("%m/%d/%y"))
            rule_amount = currency_conversion_rate*rule.amount
            if (rule.domain and self.id not in self.env['sale.order'].search(ast.literal_eval(rule.domain)).ids) or not (self.amount_total > rule_amount and (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id))):
                continue
            if rule.project_manager: 
                project = self.env['project.project'].search([('sale_line_id.order_id.id','=',self.id)])
                if project:
                    self.approver_ids = [Command.link(project.user_id.id)]

            if rule.user_id:
                self.approver_ids = [Command.link(rule.user_id.id)]
            if self.x_studio_delivery_director:
                self.approver_ids = [Command.link(self.x_studio_delivery_director.id)]
            if rule.salesperson:
                self.approver_ids = [Command.link(self.user_id.id)]
        if self.approver_ids:
            self.current_approver = self.approver_ids.ids[0]
            self._send_approval_reminder_mail('fls_approvals.email_template_validate_so')
            self.state = 'to_approve'
        else:
            self.state = 'approved'
        
    def action_approve(self):
        sudo = self.sudo()
        admin_user_group = self.env.ref('fls_approvals.accounting_administrator_access')
        if self.state != 'to_approve':
            return
        if self.current_approver_id!= self.loggedin_user_id and admin_user_group.id not in self.env.user.groups_id.ids:
            raise UserError(_('Unable to approve the record, it has to be approved by ' + self.current_approver.name+' first'))
        sudo.no_of_approvals+=1
        approvers = self.approver_ids.ids
        message = self.env.user.email_formatted+ 'has approved this Sale Order'
        self.with_user(SUPERUSER_ID).message_post(body=message)
        current_approver_index = approvers.index(self.current_approver.id)
        if len(approvers) == self.no_of_approvals:
            sudo.current_approver = None
            sudo.state = 'approved'
            self._send_approval_reminder_mail('fls_approvals.email_template_approved_so')
        else:
            sudo.current_approver = approvers[(current_approver_index+1)%len(approvers)]
            self._send_approval_reminder_mail('fls_approvals.email_template_validate_so')

    @api.depends('current_approver')
    def _compute_approver_id(self):
        for record in self:
            record.current_approver_id = record.current_approver.id

    def _compute_current_loggedin_user(self):
        for record in self:
            record.loggedin_user_id = self.env.context.get('uid', 0)
    
    def copy_data(self, default=None):
        ret = super().copy_data(default)
        for so in ret:
            so.update(current_approver = None, current_approver_id = None, approver_ids = None,no_of_approvals = 0)
        return ret
    
    def action_reject(self):
        admin_user_group = self.env.ref('fls_approvals.accounting_administrator_access')
        if self.current_approver_id!= self.loggedin_user_id and admin_user_group.id not in self.env.user.groups_id.ids:
            raise UserError(_('Unable to reject the record, it has to be rejected by ' + self.current_approver.name))
        res= {
            'name': 'Reject Entry',
            'view_mode': 'form',
            'res_model': 'approval.rejection.message',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return res
    
    def action_reject_email(self):
        self._send_approval_reminder_mail('fls_approvals.email_template_rejected_so')

    def resume_approvals(self):
        admin_user_group = self.env.ref('fls_approvals.accounting_administrator_access')
        if self.bookkeeper_id!= self.loggedin_user_id and admin_user_group.id not in self.env.user.groups_id.ids:
            raise UserError(_('Unable to resume approvals of the record, it has to be resumed by ' + self.bookkeeper_id.name))
        self.state = 'to_approve'
        self._send_approval_reminder_mail('fls_approvals.email_template_validate_so')

    def finalize(self):
        sudo = self.sudo()
        admin_user_group = self.env.ref('fls_approvals.accounting_administrator_access')
        if admin_user_group.id not in self.env.user.groups_id.ids:
            raise UserError(_('Can only be finalized by Administrator'))
        sudo.current_approver = None
        sudo.state = 'approved'
        self._send_approval_reminder_mail('fls_approvals.email_template_approved_so')
    
    def reset_approvals(self):
        for record in self:
            record.sudo().state = 'draft'
            record.approver_ids = None
            record.current_approver = None
            record.current_approver_id = None
            record.no_of_approvals = 0
