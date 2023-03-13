from odoo import models
from odoo.exceptions import AccessError


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _get_mail_thread_data(self, request_list):
        res = {'hasWriteAccess': self.env.user.has_group('fls_employee_cost.group_chatter_access'), 'hasReadAccess': True}
        if not self:
            res['hasReadAccess'] = False
            return res

        self.ensure_one()
        try:
            self.check_access_rights("write")
            self.check_access_rule("write")
            res['hasWriteAccess'] = True
        except AccessError:
            pass
        if 'activities' in request_list:
            res['activities'] = self.activity_ids.activity_format()
        if 'attachments' in request_list:
            res['attachments'] = self._get_mail_thread_data_attachments()._attachment_format()
            res['mainAttachment'] = {'id': self.message_main_attachment_id.id} if self.message_main_attachment_id else [('clear',)]
        if 'followers' in request_list:
            res['followers'] = [{
                'id': follower.id,
                'partner_id': follower.partner_id.id,
                'name': follower.name,
                'display_name': follower.display_name,
                'email': follower.email,
                'is_active': follower.is_active,
                'partner': follower.partner_id.mail_partner_format()[follower.partner_id],
            } for follower in self.message_follower_ids]
        if 'suggestedRecipients' in request_list:
            res['suggestedRecipients'] = self._message_get_suggested_recipients()[self.id]
        return res
    
    def message_unsubscribe(self, partner_ids=None):
        # return super(MailThread, self).sudo().message_unsubscribe(partner_ids)
        """ Remove partners from the records followers. """
        # not necessary for computation, but saves an access right check
        if not partner_ids:
            return True
        if set(partner_ids) == set([self.env.user.partner_id.id]):
            self.check_access_rights('read')
            self.check_access_rule('read')
        elif self.env.user.has_group('fls_employee_cost.group_chatter_access'):
            pass
        else:
            self.check_access_rights('write')
            self.check_access_rule('write')
        self.env['mail.followers'].sudo().search([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
            ('partner_id', 'in', partner_ids or []),
        ]).unlink()
    
    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        """ Main public API to add followers to a record set. Its main purpose is
        to perform access rights checks before calling ``_message_subscribe``. """
        if not self or not partner_ids:
            return True

        partner_ids = partner_ids or []
        adding_current = set(partner_ids) == set([self.env.user.partner_id.id])
        customer_ids = [] if adding_current else None

        if partner_ids and adding_current:
            try:
                self.check_access_rights('read')
                self.check_access_rule('read')
            except exceptions.AccessError:
                return False
        elif self.env.user.has_group('fls_employee_cost.group_chatter_access'):
            pass
        else:
            self.check_access_rights('write')
            self.check_access_rule('write')

        # filter inactive and private addresses
        if partner_ids and not adding_current:
            partner_ids = self.env['res.partner'].sudo().search([('id', 'in', partner_ids), ('active', '=', True), ('type', '!=', 'private')]).ids

        return self._message_subscribe(partner_ids, subtype_ids, customer_ids=customer_ids)

    def _message_update_content(self, message, body, attachment_ids=None,
                                strict=True, **kwargs):
        """ Update message content. Currently does not support attachments
        specific code (see ``_message_post_process_attachments``), to be added
        when necessary.

        Private method to use for tooling, do not expose to interface as editing
        messages should be avoided at all costs (think of: notifications already
        sent, ...).

        :param <mail.message> message: message to update, should be linked to self through
          model and res_id;
        :param str body: new body (None to skip its update);
        :param list attachment_ids: list of new attachments IDs, replacing old one (None
          to skip its update);
        :param bool strict: whether to check for allowance before updating
          content. This should be skipped only when really necessary as it
          creates issues with already-sent notifications, lack of content
          tracking, ...

        Kwargs are supported, notably to match mail.message fields to update.
        See content of this method for more details about supported keys.
        """
        self.ensure_one()
        if strict:
            self._check_can_update_message_content(message.sudo())
        msg_values = {'body': body} if body is not None else {}
        if attachment_ids:
            msg_values.update(
                self._message_post_process_attachments([], attachment_ids, {
                    'body': body,
                    'model': self._name,
                    'res_id': self.id,
                })
            )
        elif attachment_ids is not None:  # None means "no update"
            message.attachment_ids._delete_and_notify()
        if msg_values:
            message.write(msg_values)

        if 'scheduled_date' in kwargs:
            # update scheduled datetime
            if kwargs['scheduled_date']:
                self.env['mail.message.schedule'].sudo()._update_message_scheduled_datetime(
                    message,
                    kwargs['scheduled_date']
                )
            # (re)send notifications
            else:
                self.env['mail.message.schedule'].sudo()._send_message_notifications(message)

        # cleanup related message data if the message is empty
        message.sudo()._filter_empty()._cleanup_side_records()

        return self._message_update_content_after_hook(message)
    