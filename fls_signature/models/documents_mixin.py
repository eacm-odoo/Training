# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class DocumentMixin(models.AbstractModel):
    """
    Inherit this mixin to automatically create a `documents.document` when
    an `ir.attachment` is linked to a record.
    Override this mixin's methods to specify an owner, a folder or tags
    for the document.
    """
    _inherit = 'documents.mixin'
    _description = "Documents creation mixin"

    # def _get_document_vals(self, attachment):
    #     """
    #     Return values used to create a `documents.document`
    #     """
    #     self.ensure_one()
    #     document_vals = {}
    #     if self._check_create_documents():
    #         # self.request_item_ids.filtered(lambda x: x.role_id.name == 'Employee').partner_id
    #         document_vals = {
    #             'attachment_id': attachment.id,
    #             'name': attachment.name or self.display_name,
    #             'folder_id': self._get_document_folder().id,
    #             'owner_id': self._get_document_owner().id,
    #             'partner_id': self._get_document_partner().id,
    #             'tag_ids': [(6, 0, self._get_document_tags().ids)],
    #         }
    #     return document_vals

    def _get_document_partner(self):
        if self.template_id.assign_partner_to_doc:
            partner_id = self.request_item_ids.filtered(lambda x: x.role_id.name == 'Employee').partner_id
            return partner_id
        return self.env['res.partner']
