from odoo import models, fields, api, Command, _, SUPERUSER_ID
from odoo.exceptions import UserError

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
    ], ondelete={'to_approve': lambda sor: sor.write({'state': 'draft'}),'approved': lambda sor: sor.write({'state': 'draft'})})
    no_of_approvals = fields.Integer('No of Approvals')
    delivery_director = fields.Many2one('res.users')
    buyer = fields.Many2one('res.users',string = "Buyer")

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
                self.delivery_director = po.delivery_director
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

        self.state = 'to_approve'
        if not self.invoice_filter_type_domain:
            approval_rules = sorted(self.env['approval.rule'].search([('models','=','account.move'),('type','=','journal.entry')]),key = lambda x :x.sequence)
            for rule in approval_rules:
                if rule.project_manager and self.amount_total > rule.amount and (not rule.company_id or (self.company_id == rule.company_id)):
                    project = self.env['project.project'].search([('sale_line_id.order_id.id','=',self.id)])
                    if project:
                        self.approver_ids = [Command.link(project.user_id.id)]
                if rule.user_id and (not rule.company_id or (self.company_id == rule.company_id)) and self.amount_total > rule.amount:
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
                if rule.user_id and  (not rule.company_id or (self.company_id == rule.company_id)) and self.amount_total > rule.amount and (not rule.department_id or (self.department_id == rule.department_id)):
                    self.approver_ids = [Command.link(rule.user_id.id)]
                if self.buyer and rule.buyer and self.amount_total > rule.amount and  (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id)):
                    self.approver_ids = [Command.link(self.buyer.id)]
                if self.delivery_director and rule.delivery_director and po.delivery_director and self.amount_total > rule.amount and  (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id)):
                    self.approver_ids = [Command.link(self.delivery_director.id)]
                if rule.project_manager and self.amount_total > rule.amount and  (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id)):
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
                if rule.user_id and (not rule.company_id or (self.company_id == rule.company_id)) and self.amount_total > rule.amount and (not rule.department_id or (self.department_id == rule.department_id)):
                    self.approver_ids = [Command.link(rule.user_id.id)]
                if self.delivery_director and rule.delivery_director and self.amount_total > rule.amount and (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id)):
                    self.approver_ids = [Command.link(self.delivery_director.id)]
                if self.invoice_user_id and rule.salesperson and self.amount_total > rule.amount and (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id)):
                    self.approver_ids = [Command.link(self.invoice_user_id.id)]
                if rule.project_manager and self.amount_total > rule.amount and  (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id)):
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


    def action_approve(self):
        admin_user_group = self.env['res.groups'].search([('category_id.name','=','Administration'),('name','=','Access Rights')])
        if self.state != 'to_approve':
            return
        if self.current_approver_id!= self.loggedin_user_id and admin_user_group.id not in self.env.user.groups_id.ids:
            raise UserError(_('Unable to approve the record, it has to be approved by ' + self.current_approver.name+' first'))
        self.no_of_approvals+=1
        approvers = self.approver_ids.ids
        current_approver_index = approvers.index(self.current_approver.id)
        message = self.env.user.email_formatted+ 'has approved this JE'
        self.with_user(SUPERUSER_ID).message_post(body=message)
        if len(approvers) == self.no_of_approvals:
            self.current_approver = None
            self.state = 'approved'
        else:
            self.current_approver = approvers[(current_approver_index+1)%len(approvers)]
            self._send_approval_reminder_mail()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        am = super().copy(default)
        am.write({'current_approver':None, 'current_approver_id':None,'approver_ids':None,'no_of_approvals':0})
        return am
    
    def button_draft(self):
        super().button_draft()
        self.write({'current_approver':None, 'current_approver_id':None,'approver_ids':None,'no_of_approvals':0})

        

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    account_analytic = fields.Many2one(related='purchase_line_id.analytic_account')
