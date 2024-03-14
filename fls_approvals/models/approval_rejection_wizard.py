from odoo import models,fields,SUPERUSER_ID


class ApprovalRejectionMsg(models.TransientModel):
    _name='approval.rejection.message'

    rejection_reason = fields.Text(string='Rejection Reason',required=True)

    def action_submit_rejection(self):
        active_model = self.env.context.get('active_model')
        model_id = self.env.context.get('active_id')
        model = self.env[active_model].browse(model_id)
        model.sudo().write({
            'state':'rejected'
        })
        model.action_reject_email()
        model.with_user(SUPERUSER_ID).message_post(body=f"{model.name} rejected by {self.env.user.name}. Reason: {self.rejection_reason}")
        return {'type': 'ir.actions.act_window_close'}
