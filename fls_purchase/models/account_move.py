from odoo import models, fields, api
from datetime import datetime


class AccountMove(models.Model):
    _inherit = "account.move"

    date = fields.Date(compute="_compute_accounting_date", store=True)
    formatted_amount_total = fields.Char("Formatted Amount Total")
    @api.depends("line_ids")
    def _compute_accounting_date(self):
        for mv in self:
            mv.date = datetime.today()
            for line in mv.line_ids.mapped('purchase_line_id'):
                purchase_id = line.order_id
                date_planned = purchase_id.date_planned.date()
                if mv.move_type == "in_invoice" and purchase_id and date_planned:
                    mv.date = date_planned

    @api.model
    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        move_type = vals.get('move_type')
        if move_type == 'in_invoice' and not move.partner_id.is_company:
            template = self.env.ref('fls_purchase.mail_template_vendor_bill_approval', raise_if_not_found=False)
            if template:
                
                move.formatted_amount_total ="{:,}".format(5000000)
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