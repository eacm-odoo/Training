from odoo import models, fields, api


class MailFollowers(models.Model):
    _inherit = 'mail.followers'

    def _insert_followers(self, res_model, res_ids,
                            partner_ids, subtypes=None,
                            customer_ids=None, check_existing=True, existing_policy='skip'):
        if not partner_ids and self.env.context.get('block_notifications'):
            return
        return super()._insert_followers(res_model, res_ids, 
                                         partner_ids, subtypes, 
                                         customer_ids, check_existing, existing_policy)

