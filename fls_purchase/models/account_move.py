from odoo import models, fields, api
from datetime import datetime


class AccountMove(models.Model):
    _inherit = "account.move"
    
    formatted_amount_total = fields.Char("Formatted Amount Total")
    vendor_company_name = fields.Char("Vendor Company Name")

    def write(self, vals):
        for line in self.line_ids.mapped('purchase_line_id'):
            purchase_id = line.order_id
            date_planned = purchase_id.date_planned.date()
            if self.move_type == "in_invoice" and purchase_id and date_planned:
                    vals['date'] = date_planned
        res = super(AccountMove, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        move = super(AccountMove, self).create(vals)

        if move.move_type == 'in_invoice' and not move.partner_id.is_company and move.partner_id.vendor:
            employee_record = self.env['hr.employee'].search([('related_contact_ids', 'in',[move.partner_id.id] )],limit=1)
            if employee_record:
                move.vendor_company_name = employee_record.company_id.name
                template = self.env.ref('fls_purchase.mail_template_vendor_bill_approval', raise_if_not_found=False)
                if template:
                    
                    move.formatted_amount_total ="{:,}".format(move.amount_total)
                    # data = move._context.copy()
                    # pdf = self.env["ir.actions.report"].sudo()._render_qweb_pdf('account.report_invoice_with_payments',res_ids=move.ids, data=data)
                    # attachment_ids=[(0, 0, {
                    #     'name': 'vendor_bill.pdf',
                    #     'datas': pdf.encode('base64'),
                    #     'type': 'binary',
                    # })]
                    # self.with_context(is_reminder=True).message_post_with_template(template.id, email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature", composition_mode='comment',res_id=move.id,attachment_ids=attachment_ids)
                    self.with_context(is_reminder=True).message_post_with_template(template.id, email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature", composition_mode='comment',res_id=move.id)

        return move
