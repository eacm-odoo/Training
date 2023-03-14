from lxml import etree
from lxml.html import builder as html

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Invite(models.TransientModel):
    _inherit = 'mail.wizard.invite'

    def add_followers(self):
        if not self.env.user.email:
            raise UserError(_("Unable to post message, please configure the sender's email address."))
        email_from = self.env.user.email_formatted
        for wizard in self:
            Model = self.env[wizard.res_model]
            document = Model.browse(wizard.res_id)

            # filter partner_ids to get the new followers, to avoid sending email to already following partners
            new_partners = wizard.partner_ids - document.sudo().message_partner_ids
            document.message_subscribe(partner_ids=new_partners.ids)

            model_name = self.env['ir.model']._get(wizard.res_model).display_name
            # send an email if option checked and if a message exists (do not send void emails)
            if wizard.send_mail and wizard.message and not wizard.message == '<br>':  # when deleting the message, cleditor keeps a <br>
                message = self.env['mail.message'].create(
                    self._prepare_message_values(document, model_name, email_from)
                )
                email_partners_data = []
                recipients_data = self.env['mail.followers']._get_recipient_data(document, 'comment', False, pids=new_partners.ids)[document.id]
                for _pid, pdata in recipients_data.items():
                    pdata['notif'] = 'email'
                    email_partners_data.append(pdata)
                document._notify_thread_by_email(
                    message, email_partners_data,
                    send_after_commit=False
                )
                # in case of failure, the web client must know the message was
                # deleted to discard the related failure notification
                self.env['bus.bus']._sendone(self.env.user.partner_id, 'mail.message/delete', {'message_ids': message.ids})
                ##### CUSTOM CODE START #####
                message.sudo().unlink()
                #####  CUSTOM CODE END  #####
        return {'type': 'ir.actions.act_window_close'}
