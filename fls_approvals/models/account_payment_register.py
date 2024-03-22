from odoo import models, SUPERUSER_ID


class AccountPaymentRegister(models.TransientModel):
    _inherit='account.payment.register'

    def action_create_payments(self):
        action = super().action_create_payments()
        move_id = self.env.context.get('active_id')
        move = self.env['account.move'].browse(move_id)
        if move.move_type == 'in_invoice':
            move.write({'payment_registered':self.amount})
            template = self.env.ref('fls_approvals.email_template_notify_paid_bills', raise_if_not_found=False)
            if template:
                move.with_user(SUPERUSER_ID).with_context(is_reminder=True).message_post_with_template(template.id, email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature", composition_mode='comment')