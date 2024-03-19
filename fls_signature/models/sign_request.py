from odoo import models, Command

class SignRequest(models.Model):
    _inherit = 'sign.request'

    def _generate_completed_document(self, password=""):
        res = super(SignRequest, self)._generate_completed_document(password)

        customer_request_partner_id = [request_item.partner_id for request_item in self.request_item_ids if request_item.role_id.name == 'Employee']
        customer_id = customer_request_partner_id[0] if customer_request_partner_id else False

        if customer_id:
            work_contact_id_employee = self.env['hr.employee'].search([('work_contact_id.id','=',customer_id.id)])

            if not work_contact_id_employee:
                same_name_customer_ids = self.env['res.partner'].search([('name','=',customer_id.name), ('id','!=',customer_id.id)])
                same_name_customer_ids = same_name_customer_ids - customer_id
                work_contact_id_employee = self.env['hr.employee'].search([('work_contact_id.id','=',customer_id.id)])

            if not work_contact_id_employee:
                work_contact_id_employee = self.env['hr.employee'].search([('work_email','=',customer_id.email)])
            
            # if work_contact_id_employee:
                

                # work_contact_id_employee.signed_document = [Command.link(attachment_id.id)]
                

        return res
