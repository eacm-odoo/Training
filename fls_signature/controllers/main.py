from odoo import http
from odoo.addons.sign.controllers import main

class Sign(main.Sign):
    @http.route(["/sign/document/<int:sign_request_id>/<token>"], type='http', auth='public', website=True)

    def sign_document_public(self, sign_request_id, token, **post):
        # action = super(Sign, self).sign_document_public(sign_request_id, token, **post)
        document_context = self.get_document_qweb_context(sign_request_id, token, **post)
        if not isinstance(document_context, dict):
            return document_context

        current_request_item = document_context.get('current_request_item')
        if current_request_item and current_request_item.partner_id.lang:
            http.request.env.context = dict(http.request.env.context, lang=current_request_item.partner_id.lang)
        return http.request.render('sign.doc_sign', document_context)
        return action
