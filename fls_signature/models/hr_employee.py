from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    first_name = fields.Char(string='First Name', compute='_compute_first_name')
    last_name = fields.Char(string='Last Name', compute='_compute_last_name')

    signed_document = fields.Many2many('ir.attachment', string='Signed Documents', help="Documents that have been signed by this employee")
    address_home_complete = fields.Char(string='Complete Address', compute='_compute_address_complete')
    country_name = fields.Char(string='Country', related='country_id.name', store=True)

    def _compute_address_complete(self):
        for employee in self:
            employee.address_home_complete = "%s, %s, %s, %s, %s" % (employee.address_home_id.street, employee.address_home_id.city, employee.address_home_id.state_id.name, employee.address_home_id.country_id.name, employee.address_home_id.zip)

    def _compute_first_name(self):
        for record in self:
            if not record.name:
                record['first_name'] = ""
            elif record.name.strip().rfind(" ") != -1:
                record['first_name'] = record.name.strip()[:record.name.strip().rfind(" ")].strip()
            else:
                record['first_name'] = ""

    def _compute_last_name(self):
        for record in self:
            if not record.name:
                record['last_name'] = ""
            elif record.name.strip().rfind(" ") != -1:
                record['last_name'] = record.name.strip()[record.name.strip().rfind(" "):].strip()
            else:
                record['last_name'] = record.name.strip()
