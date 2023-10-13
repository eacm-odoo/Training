from odoo import fields, models, Command, api, _ , SUPERUSER_ID
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
    department_id = fields.Many2one('hr.department', string='Department')
    no_of_approvals = fields.Integer('No of Approvals')
    def _send_approval_reminder_mail(self):
        template = self.env.ref('fls_approvals.email_template_validate_so', raise_if_not_found=False)
        if template:
            self.with_user(SUPERUSER_ID).with_context(is_reminder=True).message_post_with_template(template.id, email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature", composition_mode='comment')

    def action_send_validate_so_email(self):
        self.state = 'to_approve'

        approval_rules = sorted(self.env['approval.rule'].search([('models','=','sale.order')]),key = lambda x :x.sequence)
        for rule in approval_rules:
            if rule.project_manager and self.amount_total > rule.amount and (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id)): 
                project = self.env['project.project'].search([('sale_line_id.order_id.id','=',self.id)])
                if project:
                    self.approver_ids = [Command.link(project.user_id.id)]

            if (not rule.company_id or (self.company_id == rule.company_id)) and self.amount_total > rule.amount and rule.user_id and (not rule.department_id or (self.department_id == rule.department_id)):
                self.approver_ids = [Command.link(rule.user_id.id)]
            if rule.delivery_director and self.amount_total > rule.amount and (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id)):
                self.approver_ids = [Command.link(self.x_studio_delivery_director.id)]
            if rule.salesperson and self.amount_total > rule.amount and (not rule.company_id or (self.company_id == rule.company_id)) and (not rule.department_id or (self.department_id == rule.department_id)):
                self.approver_ids = [Command.link(self.user_id.id)]
        if self.approver_ids:
            self.current_approver = self.approver_ids.ids[0]
            self._send_approval_reminder_mail()
        else:
            self.state = 'approved'
    
    def action_approve(self):
        if self.state != 'to_approve':
            return
        if self.current_approver_id!= self.loggedin_user_id:
            raise UserError(_('Unable to Approver Record, This record has to be approved by ' + self.current_approver.name))
        self.no_of_approvals+=1
        approvers = self.approver_ids.ids
        message = self.current_approver.email_formatted+ 'has approved this Sale Order'
        self.with_user(SUPERUSER_ID).message_post(body=message)
        current_approver_index = approvers.index(self.current_approver.id)
        if len(approvers) == self.no_of_approvals:
            self.current_approver = None
            self.state = 'approved'
        else:
            self.current_approver = approvers[(current_approver_index+1)%len(approvers)]
            self._send_approval_reminder_mail()

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
