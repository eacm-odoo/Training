from odoo import models, fields
from odoo.exceptions import AccessError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    additional_note = fields.Text(string='Additional Note', groups="hr.group_hr_user", tracking=False)
    address_home_id = fields.Many2one(
        'res.partner', 'Address', help='Enter here the private address of the employee, not the one linked to your company.',
        groups="hr.group_hr_user", tracking=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account Number',
        domain="[('partner_id', '=', address_home_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        groups="hr.group_hr_user",
        tracking=False,
        help='Employee bank account to pay salaries')
    birthday = fields.Date('Date of Birth', groups="hr.group_hr_user", tracking=False)
    certificate = fields.Selection([
        ('graduate', 'Graduate'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
    ], 'Certificate Level', default='other', groups="hr.group_hr_user", tracking=False)
    children = fields.Integer(string='Number of Dependent Children', groups="hr.group_hr_user", tracking=False)
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)', groups="hr.group_hr_user", tracking=False)
    country_of_birth = fields.Many2one('res.country', string="Country of Birth", groups="hr.group_hr_user", tracking=False)
    departure_date = fields.Date(string="Departure Date", groups="hr.group_hr_user", copy=False, tracking=False)    
    emergency_contact = fields.Char("Contact Name", groups="hr.group_hr_user", tracking=False)
    emergency_phone = fields.Char("Contact Phone", groups="hr.group_hr_user", tracking=False)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups="hr.group_hr_user", tracking=False)
    work_permit_expiration_date = fields.Date('Work Permit Expiration Date', groups="hr.group_hr_user", tracking=False)
    has_work_permit = fields.Binary(string="Work Permit", groups="hr.group_hr_user", tracking=False)
    identification_id = fields.Char(string='Identification No', groups="hr.group_hr_user", tracking=False)
    km_home_work = fields.Integer(string="Home-Work Distance", groups="hr.group_hr_user", tracking=False)
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups="hr.group_hr_user", default='single', tracking=False)
    passport_id = fields.Char('Passport No', groups="hr.group_hr_user", tracking=False)
    permit_no = fields.Char('Work Permit No', groups="hr.group_hr_user", tracking=False)
    phone = fields.Char(related='address_home_id.phone', related_sudo=False, readonly=False, string="Private Phone", groups="hr.group_hr_user", tracking=False)
    place_of_birth = fields.Char('Place of Birth', groups="hr.group_hr_user", tracking=False)
    private_email = fields.Char(related='address_home_id.email', string="Private Email", groups="hr.group_hr_user", tracking=False)
    ssnid = fields.Char('SSN No', help='Social Security Number', groups="hr.group_hr_user", tracking=False)
    sinid = fields.Char('SIN No', help='Social Insurance Number', groups="hr.group_hr_user", tracking=False)
    spouse_complete_name = fields.Char(string="Spouse Complete Name", groups="hr.group_hr_user", tracking=False)
    spouse_birthdate = fields.Date(string="Spouse Birthdate", groups="hr.group_hr_user", tracking=False)
    study_field = fields.Char("Field of Study", groups="hr.group_hr_user", tracking=False)
    study_school = fields.Char("School", groups="hr.group_hr_user", tracking=False)
    visa_no = fields.Char('Visa No', groups="hr.group_hr_user", tracking=False)
    visa_expire = fields.Date('Visa Expire Date', groups="hr.group_hr_user", tracking=False)