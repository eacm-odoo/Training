from odoo import models
from odoo.exceptions import AccessError


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _get_mail_thread_data(self, request_list):
        ##### CUSTOM CODE START #####
        res = {'hasWriteAccess': self.env.user.has_group('fls_mail_access.group_chatter_access'), 'hasReadAccess': True}
        #####  CUSTOM CODE END  #####
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
        ##### CUSTOM CODE START #####
        if self.env.user.has_group('fls_mail_access.group_chatter_access'):
            pass
        #####  CUSTOM CODE END  #####
        elif set(partner_ids) == set([self.env.user.partner_id.id]):
            self.check_access_rights('read')
            self.check_access_rule('read')
        else:
            self.check_access_rights('write')
            self.check_access_rule('write')
        self.env['mail.followers'].sudo().search([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
            ('partner_id', 'in', partner_ids or []),
        ]).unlink()
    
    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        if not self or not partner_ids:
            return True

        partner_ids = partner_ids or []
        adding_current = set(partner_ids) == set([self.env.user.partner_id.id])
        customer_ids = [] if adding_current else None

        ##### CUSTOM CODE START #####
        if self.env.user.has_group('fls_mail_access.group_chatter_access'):
            pass
        #####  CUSTOM CODE END  #####
        elif partner_ids and adding_current:
            try:
                self.check_access_rights('read')
                self.check_access_rule('read')
            except exceptions.AccessError:
                return False
        else:
            self.check_access_rights('write')
            self.check_access_rule('write')

        # filter inactive and private addresses
        if partner_ids and not adding_current:
            partner_ids = self.env['res.partner'].sudo().search([('id', 'in', partner_ids), ('active', '=', True), ('type', '!=', 'private')]).ids

        return self._message_subscribe(partner_ids, subtype_ids, customer_ids=customer_ids)

