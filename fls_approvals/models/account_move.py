from odoo import models, fields, api, Command, _, SUPERUSER_ID
from odoo.exceptions import UserError
import ast
class AccountMove(models.Model):
    _inherit = 'account.move'

    approver_ids = fields.Many2many('res.users', string='Approvers')
    current_approver = fields.Many2one('res.users',string = 'Current Approver')
    current_approver_id = fields.Integer('Current Approver Id', compute = '_compute_approver_id')
    loggedin_user_id = fields.Integer('Loggedin User', compute = '_compute_current_loggedin_user')
    department_id = fields.Many2one('hr.department', string='Department')
    state = fields.Selection(selection_add=[
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('rejected','Rejected')
    ], ondelete={'to_approve': lambda sor: sor.write({'state': 'draft'}),'approved': lambda sor: sor.write({'state': 'draft'}),'rejected': lambda sor: sor.write({'state': 'draft'})})
    no_of_approvals = fields.Integer('No of Approvals')
    delivery_director = fields.Many2one('res.users')
    buyer = fields.Many2one('res.users',string = "Buyer")
    bookkeeper_id = fields.Many2one('res.users',string='Bookkeeper')
    submitter = fields.Many2one('res.users',string='Submitter')

    @api.model_create_multi
    def create(self, vals):
        moves = super().create(vals)
        for move in moves: 
            if move.invoice_filter_type_domain == 'sale':
                so = self.env['sale.order'].search([('name','=',move.invoice_origin)])
                move.delivery_director = so.x_studio_delivery_director
                move.department_id = so.department_id
            if move.invoice_filter_type_domain == 'purchase':
                po = self.env['purchase.order'].search([('name','=',move.invoice_origin)])
                move.buyer = po.user_id.id
                move.department_id = po.department_id
                move.delivery_director = po.delivery_director
                if move.invoice_source_email: 
                    template = self.env.ref('fls_approvals.email_template_notify_admin_bills', raise_if_not_found=False)
                    if template:
                        move.with_user(SUPERUSER_ID).with_context(is_reminder=True).message_post_with_template(template.id, email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature", composition_mode='comment')

                
        return moves

    def _send_approval_reminder_mail(self):
        if not self.invoice_filter_type_domain:
            template = self.env.ref('fls_approvals.email_template_validate_je', raise_if_not_found=False)
        if self.invoice_filter_type_domain == 'sale':
            template = self.env.ref('fls_approvals.email_template_validate_inv', raise_if_not_found=False)
        if self.invoice_filter_type_domain == 'purchase':
            template = self.env.ref('fls_approvals.email_template_validate_bills', raise_if_not_found=False)
        if template:
            self.with_user(SUPERUSER_ID).with_context(is_reminder=True).message_post_with_template(template.id, email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature", composition_mode='comment')

    @api.depends('current_approver')
    def _compute_approver_id(self):
        for record in self:
            record.current_approver_id = record.current_approver.id

    def _compute_current_loggedin_user(self):
        for record in self:
            record.loggedin_user_id = self.env.context.get('uid', 0)
    def action_send_validate_je_email(self):

        if not self.invoice_filter_type_domain:
            approval_rules = sorted(self.env['approval.rule'].search([('models','=','account.move'),('type','=','journal.entry')]),key = lambda x :x.sequence)
            for rule in approval_rules:
                currency_conversion_rate = self.env['res.currency']._get_conversion_rate(rule.company_id.currency_id if rule.company_id else self.env['res.currency'].search([('name','=','USD')], limit=1),self.currency_id,self.company_id,self.date.strftime("%m/%d/%y"))
                rule_amount = currency_conversion_rate*rule.amount
                if rule.domain and self.id not in self.env['account.move'].search(ast.literal_eval(rule.domain)).ids or not( self.amount_total > rule_amount and (not rule.company_id or (self.company_id == rule.company_id))):
                    continue                  
                if rule.project_manager:
                    project = self.env['project.project'].search([('sale_line_id.order_id.id','=',self.id)])
                    if project:
                        self.approver_ids = [Command.link(project.user_id.id)]
                if rule.user_id:
                    self.approver_ids = [Command.link(rule.user_id.id)]
            if self.approver_ids:
                self.current_approver = self.approver_ids.ids[0]
                self._send_approval_reminder_mail()
            else:
                self.state = 'approved'
        if self.invoice_filter_type_domain == 'purchase':
            po = self.env['purchase.order'].search([('name','=',self.invoice_origin)])
            approval_rules = sorted(self.env['approval.rule'].search([('models','=','account.move'),('type','=','vendor.bill')]),key = lambda x :x.sequence)
            for rule in approval_rules:
                currency_conversion_rate = self.env['res.currency']._get_conversion_rate(rule.company_id.currency_id if rule.company_id else self.env['res.currency'].search([('name','=','USD')], limit=1) ,self.currency_id,self.company_id,self.date.strftime("%m/%d/%y"))
                rule_amount = currency_conversion_rate*rule.amount
                if rule.domain and self.id not in self.env['account.move'].search(ast.literal_eval(rule.domain)).ids or not(self.amount_total > rule_amount and  (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id))):
                    continue   
                if rule.user_id:
                    self.approver_ids = [Command.link(rule.user_id.id)]
                if self.buyer and rule.buyer:
                    self.approver_ids = [Command.link(self.buyer.id)]
                if self.delivery_director and rule.delivery_director:
                    self.approver_ids = [Command.link(self.delivery_director.id)]
                if rule.project_manager:
                    move_line_ids = self.line_ids
                    for line in move_line_ids:
                        if line.account_analytic:
                            if line.account_analytic.project_ids:
                                projects = line.account_analytic.project_ids
                                self.approver_ids = [Command.link(projects[0].user_id.id)]
                                break
                if po.timesheet_approver_id and rule.timesheet_approver and self.amount_total > rule.amount and  (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id)):
                    self.approver_ids = [Command.link(po.timesheet_approver_id.id)]
                
            if self.approver_ids:
                self.current_approver = self.approver_ids.ids[0]
                self._send_approval_reminder_mail()
            else:
                self.state = 'approved'
        if self.invoice_filter_type_domain == 'sale':
            so = self.env['sale.order'].search([('name','=',self.invoice_origin)])
            approval_rules = sorted(self.env['approval.rule'].search([('models','=','account.move'),('type','=','sale.invoice')]),key = lambda x :x.sequence)
            for rule in approval_rules:
                currency_conversion_rate = self.env['res.currency']._get_conversion_rate(rule.company_id.currency_id if rule.company_id else self.env['res.currency'].search([('name','=','USD')], limit=1),self.currency_id,self.company_id,self.date_order.strftime("%m/%d/%y"))
                rule_amount = currency_conversion_rate*rule.amount
                if rule.domain and self.id not in self.env['account.move'].search(ast.literal_eval(rule.domain)).ids or not(self.amount_total > rule_amount and (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id))):
                    continue  
                if rule.user_id:
                    self.approver_ids = [Command.link(rule.user_id.id)]
                if self.delivery_director and rule.delivery_director:
                    self.approver_ids = [Command.link(self.delivery_director.id)]
                if self.invoice_user_id and rule.salesperson:
                    self.approver_ids = [Command.link(self.invoice_user_id.id)]
                if rule.project_manager:
                    move_line_ids = self.line_ids
                    for line in move_line_ids:                        
                        if so.analytic_account_id and so.analytic_account_id.project_ids :
                            projects = so.analytic_account_id.project_ids
                            self.approver_ids = [Command.link(projects[0].user_id.id)]
                            break
            if self.approver_ids:
                self.current_approver = self.approver_ids.ids[0]
                self._send_approval_reminder_mail()
            else:
                self.state = 'approved'
        self.state = 'to_approve' if self.state != 'approved' else 'approved'
    def send_approved_email(self):
        if not self.invoice_filter_type_domain:
            template = self.env.ref('fls_approvals.email_template_approved_je', raise_if_not_found=False)
        if self.invoice_filter_type_domain == 'sale':
            template = self.env.ref('fls_approvals.email_template_approved_inv', raise_if_not_found=False)
        if self.invoice_filter_type_domain == 'purchase':
            template = self.env.ref('fls_approvals.email_template_approved_bills', raise_if_not_found=False)
        if template:
            self.with_user(SUPERUSER_ID).with_context(is_reminder=True).message_post_with_template(template.id, email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature", composition_mode='comment')
    
    def send_rejected_email(self):
        if not self.invoice_filter_type_domain:
            template = self.env.ref('fls_approvals.email_template_rejected_je', raise_if_not_found=False)
        if self.invoice_filter_type_domain == 'sale':
            template = self.env.ref('fls_approvals.email_template_rejected_inv', raise_if_not_found=False)
        if self.invoice_filter_type_domain == 'purchase':
            template = self.env.ref('fls_approvals.email_template_rejected_bills', raise_if_not_found=False)
        if template:
            self.with_user(SUPERUSER_ID).with_context(is_reminder=True).message_post_with_template(template.id, email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature", composition_mode='comment')
    def action_approve(self):
        sudo = self.sudo()
        admin_user_group = self.env.ref('fls_approvals.accounting_administrator_access')
        if self.state != 'to_approve':
            return
        if self.current_approver_id!= self.loggedin_user_id and admin_user_group.id not in self.env.user.groups_id.ids:
            raise UserError(_('Unable to approve the record, it has to be approved by ' + self.current_approver.name+' first'))
        sudo.no_of_approvals+=1
        approvers = self.approver_ids.ids
        current_approver_index = approvers.index(self.current_approver.id)
        message = self.env.user.email_formatted+ 'has approved this JE'
        self.with_user(SUPERUSER_ID).message_post(body=message)
        if len(approvers) == self.no_of_approvals:
            sudo.current_approver = None
            sudo.state = 'approved'
            sudo.send_approved_email()
        else:
            sudo.current_approver = approvers[(current_approver_index+1)%len(approvers)]
            self._send_approval_reminder_mail()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        am = super().copy(default)
        am.write({'current_approver':None, 'current_approver_id':None,'approver_ids':None,'no_of_approvals':0})
        return am
    
    def button_draft(self):
        self.sudo().state='rejected'
        super().button_draft()
        self.write({'current_approver':None, 'current_approver_id':None,'approver_ids':None,'no_of_approvals':0})
    
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
        self.send_rejected_email()

    def resume_approvals(self):
        admin_user_group = self.env.ref('fls_approvals.accounting_administrator_access')
        if self.bookkeeper_id.id!= self.loggedin_user_id and admin_user_group.id not in self.env.user.groups_id.ids:
            raise UserError(_('Unable to resume approvals of the record, it has to be resumed by ' + self.bookkeeper_id.name))
        self.state = 'to_approve'
        self._send_approval_reminder_mail()

    def finalize(self):
        sudo = self.sudo()
        admin_user_group = self.env.ref('fls_approvals.accounting_administrator_access')
        if admin_user_group.id not in self.env.user.groups_id.ids:
            raise UserError(_('Can only be finalized by Administrator'))
        sudo.current_approver = None
        sudo.state = 'approved'
        self.send_approved_email()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    account_analytic = fields.Many2one(related='purchase_line_id.analytic_account')
