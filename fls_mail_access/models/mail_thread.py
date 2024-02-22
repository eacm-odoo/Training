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

    def _message_auto_subscribe(self, updated_values, followers_existing_policy='skip'):
        if not self:
            return True

        new_partner_subtypes = dict()
        updated_relation = dict()
        child_ids, def_ids, all_int_ids, parent, relation = self.env['mail.message.subtype']._get_auto_subscription_subtypes(self._name)

        for res_model, fnames in relation.items():
            for field in (fname for fname in fnames if updated_values.get(fname)):
                updated_relation.setdefault(res_model, set()).add(field)
        updated_fields = [fname for fnames in updated_relation.values() for fname in fnames if updated_values.get(fname)]

        if updated_fields:
            doc_data = [(model, [updated_values[fname] for fname in fnames]) for model, fnames in updated_relation.items()]
            res = self.env['mail.followers']._get_subscription_data(doc_data, None, include_pshare=True, include_active=True)
            for _fol_id, _res_id, partner_id, subtype_ids, pshare, active in res:
                sids = [parent[sid] for sid in subtype_ids if parent.get(sid)]
                sids += [sid for sid in subtype_ids if sid not in parent and sid in child_ids]
                if partner_id and active:
                    if pshare:
                        new_partner_subtypes[partner_id] = set(sids) - set(all_int_ids)
                    else:
                        new_partner_subtypes[partner_id] = set(sids)

        notify_data = dict()
        template_blacklist = ['mail.message_user_assigned']

        res = self._message_auto_subscribe_followers(updated_values, def_ids)
        for partner_id, sids, template in res:
            if template not in template_blacklist:
                new_partner_subtypes.setdefault(partner_id, sids)
                if template:
                    partner = self.env['res.partner'].browse(partner_id)
                    lang = partner.lang if partner else None
                    notify_data.setdefault((template, lang), list()).append(partner_id)

        if new_partner_subtypes:
            self.env['mail.followers']._insert_followers(
                self._name, self.ids,
                list(new_partner_subtypes), subtypes=new_partner_subtypes,
                check_existing=True, existing_policy=followers_existing_policy)

        for (template, lang), pids in notify_data.items():
            if template not in template_blacklist:
                self.with_context(lang=lang)._message_auto_subscribe_notify(pids, template)

        return True

