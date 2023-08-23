from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    timesheet_approver_id = fields.Many2one('res.user', string="Timesheet Approver", compute="_compute_timesheet_approver")

    @api.depends("partner_id", "partner_id.employee_ids", "partner_id.employee_ids.timesheet_manager_id")
    def _compute_timesheet_approver(self):
        for order in self:
            for employee in order.partner_id.employee_ids:
                if employee.timesheet_manager_id:
                    order.timesheet_approver_id = employee.timesheet_manager_id.id
                    break

    def _send_rfq_approval_reminder_mail(self):
        template = self.env.ref('fls_purchase.mail_template_purchase_approval', raise_if_not_found=False)
        if template:
            self.with_context(is_reminder=True).message_post_with_template(template.id, email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature", composition_mode='comment')
