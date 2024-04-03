from odoo import models, fields, api, Command, _, SUPERUSER_ID
from odoo.exceptions import UserError
import ast
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approver_ids = fields.Many2many('res.approvers', string='Approvers')
    state = fields.Selection(selection_add=[
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('purchase','Purchase Order'),
        ('rejected', 'Rejected')

    ])
    current_approver = fields.Many2one('res.users',string = 'Current Approver')
    current_approver_id = fields.Integer('Current Approver Id', compute = '_compute_approver_id',store = True)
    loggedin_user_id = fields.Integer('Loggedin User', compute = '_compute_current_loggedin_user')
    department_id = fields.Many2one('hr.department', string='Department')
    delivery_director = fields.Many2one('res.users',string = 'Delivery Director')
    no_of_approvals = fields.Integer('No of Approvals')
    bookkeeper_id = fields.Many2one('res.users',string='Bookkeeper',default=lambda self: self.env.user.id,required = True)

    def _send_approval_reminder_mail(self,template_name):
        template = self.env.ref(template_name, raise_if_not_found=False)
        if template:
            self.with_user(SUPERUSER_ID).with_context(is_reminder=True).message_post_with_template(template.id, email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature", composition_mode='comment')

    def action_send_validate_po_email(self):
        
        approver = self.env['res.approvers']
        approval_rules = sorted(self.env['approval.rule'].search([('models','=','purchase.order')]),key = lambda x :x.sequence)
        for rule in approval_rules:
            currency_id = rule.company_id.currency_id or self.env.ref('base.USD')
            currency_conversion_rate = self.env['res.currency']._get_conversion_rate(currency_id,self.currency_id,self.company_id,self.date_order.strftime("%m/%d/%y"))
            domain = ast.literal_eval(rule.domain)
            domain = rule.convert_currency_in_domain_filter(domain,currency_conversion_rate)
            if rule.domain and self.id not in self.env['purchase.order'].search(domain).ids or not (not rule.company_id or (self.company_id == rule.company_id)):
                continue            
            if rule.user_id:
                self.approver_ids = [Command.link(approver.create({'approver_id':rule.user_id.id}).id)]
            if rule.buyer: 
                self.approver_ids = [Command.link(approver.create({'approver_id':self.user_id.id}).id)]
            if self.timesheet_approver_id and rule.timesheet_approver: 
                self.approver_ids = [Command.link(approver.create({'approver_id':self.timesheet_approver_id.id}).id)]
            if self.delivery_director and rule.delivery_director: 
                self.approver_ids = [Command.link(approver.create({'approver_id':self.delivery_director.id}).id)]
        if self.approver_ids:
            self.current_approver = self.approver_ids[0].approver_id.id
            self._send_approval_reminder_mail('fls_approvals.email_template_validate_po')
            self.state = 'to_approve'

        else:
            self.state = 'approved'
    
    @api.depends('current_approver')
    def _compute_approver_id(self):
        for record in self:
            record.current_approver_id = record.current_approver.id

    def _compute_current_loggedin_user(self):
        for record in self:
            record.loggedin_user_id = self.env.context.get('uid', 0)
    
    def action_approve(self):
        sudo = self.sudo()
        user_in_accounting_admin = self.env.user.has_group('fls_approvals.accounting_administrator_access')
        if self.state != 'to_approve':
            return
        if self.current_approver_id!= self.loggedin_user_id  and not user_in_accounting_admin:
            raise UserError(_('Unable to approve the record, it has to be approved by ' + self.current_approver.name+' first'))
        sudo.no_of_approvals+=1

        approvers = self.approver_ids.ids
        message = self.env.user.email_formatted+ 'has approved this Purchase Order'
        self.with_user(SUPERUSER_ID).message_post(body=message)
        current_approval_record = self.approver_ids.filtered(lambda x : x.approver_id == self.current_approver).id
        current_approver_index = approvers.index(current_approval_record)
        if len(approvers) == self.no_of_approvals:
            sudo.current_approver = None
            sudo.state = 'approved'
            self._send_approval_reminder_mail('fls_approvals.email_template_approved_po')
        else:
            sudo.current_approver = self.approver_ids[(current_approver_index+1)%len(approvers)].approver_id.id
            self._send_approval_reminder_mail('fls_approvals.email_template_validate_po')

    def copy(self, default=None):
        new_po = super().copy(default)
        new_po.write({'current_approver':None, 'current_approver_id':None,'approver_ids':None,'no_of_approvals':0})
        return new_po
    
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent','approved']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True
    
    def action_reject(self):
        user_in_accounting_admin = self.env.user.has_group('fls_approvals.accounting_administrator_access')
        if self.current_approver_id!= self.loggedin_user_id and not user_in_accounting_admin:
            raise UserError(_('Unable to reject the record, it has to be rejected by ' + self.current_approver.name))
        res= {
            'name': 'Reject Entry',
            'view_mode': 'form',
            'res_model': 'approval.rejection.message',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return res

    def resume_approvals(self):
        user_in_accounting_admin = self.env.user.has_group('fls_approvals.accounting_administrator_access')
        if self.bookkeeper_id!= self.loggedin_user_id and not user_in_accounting_admin:
            raise UserError(_('Unable to resume approvals of the record, it has to be resumed by ' + self.bookkeeper_id.name))
        self.state = 'to_approve'
        self._send_approval_reminder_mail('fls_approvals.email_template_validate_po')
    
    def action_reject_email(self):
        self._send_approval_reminder_mail('fls_approvals.email_template_rejected_po')
    
    def finalize(self):
        sudo = self.sudo()
        user_in_accounting_admin = self.env.user.has_group('fls_approvals.accounting_administrator_access')
        if not user_in_accounting_admin:
            raise UserError(_('Can only be finalized by Administrator'))
        sudo.current_approver = None
        sudo.state = 'approved'
        self._send_approval_reminder_mail('fls_approvals.email_template_approved_po')
    
    def reset_approvals(self):
        for record in self:
            record.sudo().state = 'draft'
            record.approver_ids = None
            record.current_approver = None
            record.current_approver_id = None
            record.no_of_approvals = 0

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    analytic_account = fields.Many2one('account.analytic.account',string = 'Account_Analytic')
