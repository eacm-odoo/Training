from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_auto_subscribe(self, updated_values, followers_existing_policy='skip'):
        self = self.with_context(block_notifications=True)
        return super()._message_auto_subscribe(updated_values, followers_existing_policy=followers_existing_policy) 

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        template_blacklist = ['mail.message_user_assigned']
        followers = super()._message_auto_subscribe_followers(updated_values, default_subtype_ids)
        if self.env.context.get('block_notifications'):
            return [follower for follower in followers if follower[2] not in template_blacklist]
        return followers
