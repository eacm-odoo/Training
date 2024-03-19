from odoo import models, fields, tools, api

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


class FLSHrEmployee(models.Model):
    _name = 'hr.employee.fls.hr'
    _inherit = 'hr.employee'
    _auto = False

    employee_id = fields.Many2one('hr.employee', 'Employee', compute="_compute_employee_id", search="_search_employee_id", compute_sudo=True)

    child_ids = fields.One2many('hr.employee.public', 'parent_id', string='Direct subordinates', readonly=True)
    image_1920 = fields.Image("Image", related='employee_id.image_1920', compute_sudo=True)
    image_1024 = fields.Image("Image 1024", related='employee_id.image_1024', compute_sudo=True)
    image_512 = fields.Image("Image 512", related='employee_id.image_512', compute_sudo=True)
    image_256 = fields.Image("Image 256", related='employee_id.image_256', compute_sudo=True)
    image_128 = fields.Image("Image 128", related='employee_id.image_128', compute_sudo=True)
    avatar_1920 = fields.Image("Avatar", related='employee_id.avatar_1920', compute_sudo=True)
    avatar_1024 = fields.Image("Avatar 1024", related='employee_id.avatar_1024', compute_sudo=True)
    avatar_512 = fields.Image("Avatar 512", related='employee_id.avatar_512', compute_sudo=True)
    avatar_256 = fields.Image("Avatar 256", related='employee_id.avatar_256', compute_sudo=True)
    avatar_128 = fields.Image("Avatar 128", related='employee_id.avatar_128', compute_sudo=True)
    parent_id = fields.Many2one('hr.employee.public', 'Manager', readonly=True)
    coach_id = fields.Many2one('hr.employee.public', 'Coach', readonly=True)
    user_partner_id = fields.Many2one(related='user_id.partner_id', related_sudo=False, string="User's partner")

    mobile_phone=fields.Char(readonly=False)
    work_phone=fields.Char(readonly=False)
    work_email=fields.Char(readonly=False)
    department_id=fields.Many2one(readonly=False)
    job_id=fields.Many2one(readonly=False)
    employee_type=fields.Selection(readonly=False)
    # company_id=fields.Many2one(readonly=False)
    parent_id=fields.Many2one(readonly=False)
    coach_id=fields.Many2one(readonly=False)

    def _compute_employee_id(self):
        for employee in self:
            employee.employee_id = self.env['hr.employee'].browse(employee.id)


    # private_employee_id = fields.Many2one('hr.employee', auto_join=True, index=True, ondelete="cascade", required=True)
    # public_employee_id = fields.Many2one('hr.employee.public', required=True, ondelete='cascade')

    # Fields coming from hr.employee.base
    # create_date = fields.Datetime(readonly=True)
    # name = fields.Char(readonly=True)
    # active = fields.Boolean(readonly=True)
    # department_id = fields.Many2one(readonly=True)
    # job_id = fields.Many2one(readonly=True)
    # job_title = fields.Char(readonly=True)
    # company_id = fields.Many2one(readonly=True)
    # address_id = fields.Many2one(readonly=True)
    # mobile_phone = fields.Char(readonly=True)
    # work_phone = fields.Char(readonly=True)
    # work_email = fields.Char(readonly=True)
    # work_contact_id = fields.Many2one(readonly=True)
    # related_contact_ids = fields.Many2many(readonly=True)
    # work_location_id = fields.Many2one(readonly=True)
    # user_id = fields.Many2one(readonly=True)
    # resource_id = fields.Many2one(readonly=True)
    # resource_calendar_id = fields.Many2one(readonly=True)
    # tz = fields.Selection(readonly=True)
    # color = fields.Integer(readonly=True)
    # employee_type = fields.Selection(readonly=True)


    # fields coming from hr.employee
    # name = fields.Char(string="Employee Name", related='resource_id.name', store=True, readonly=False, tracking=True)
    # user_id = fields.Many2one('res.users', 'User', related='resource_id.user_id', store=True, readonly=False)
    # user_partner_id = fields.Many2one(related='user_id.partner_id', related_sudo=False, string="User's partner")
    # active = fields.Boolean('Active', related='resource_id.active', default=True, store=True, readonly=False)
    # company_id = fields.Many2one('res.company', required=True)
    # company_country_id = fields.Many2one('res.country', 'Company Country', related='company_id.country_id', readonly=True)
    # company_country_code = fields.Char(related='company_country_id.code', depends=['company_country_id'], readonly=True)
    # # private partner
    # address_home_id = fields.Many2one(
    #     'res.partner', 'Address', help='Enter here the private address of the employee, not the one linked to your company.',
    #     groups="hr.group_hr_user", tracking=True,
    #     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    # is_address_home_a_company = fields.Boolean(
    #     'The employee address has a company linked',
    #     compute='_compute_is_address_home_a_company',
    # )
    # private_email = fields.Char(related='address_home_id.email', string="Private Email", groups="hr.group_hr_user")
    # lang = fields.Selection(related='address_home_id.lang', string="Lang", groups="hr.group_hr_user", readonly=False)
    # country_id = fields.Many2one(
    #     'res.country', 'Nationality (Country)', groups="hr.group_hr_user", tracking=True)
    # gender = fields.Selection([
    #     ('male', 'Male'),
    #     ('female', 'Female'),
    #     ('other', 'Other')
    # ], groups="hr.group_hr_user", tracking=True)
    # marital = fields.Selection([
    #     ('single', 'Single'),
    #     ('married', 'Married'),
    #     ('cohabitant', 'Legal Cohabitant'),
    #     ('widower', 'Widower'),
    #     ('divorced', 'Divorced')
    # ], string='Marital Status', groups="hr.group_hr_user", default='single', tracking=True)
    # spouse_complete_name = fields.Char(string="Spouse Complete Name", groups="hr.group_hr_user", tracking=True)
    # spouse_birthdate = fields.Date(string="Spouse Birthdate", groups="hr.group_hr_user", tracking=True)
    # children = fields.Integer(string='Number of Dependent Children', groups="hr.group_hr_user", tracking=True)
    # place_of_birth = fields.Char('Place of Birth', groups="hr.group_hr_user", tracking=True)
    # country_of_birth = fields.Many2one('res.country', string="Country of Birth", groups="hr.group_hr_user", tracking=True)
    # birthday = fields.Date('Date of Birth', groups="hr.group_hr_user", tracking=True)
    # ssnid = fields.Char('SSN No', help='Social Security Number', groups="hr.group_hr_user", tracking=True)
    # sinid = fields.Char('SIN No', help='Social Insurance Number', groups="hr.group_hr_user", tracking=True)
    # identification_id = fields.Char(string='Identification No', groups="hr.group_hr_user", tracking=True)
    # passport_id = fields.Char('Passport No', groups="hr.group_hr_user", tracking=True)
    # bank_account_id = fields.Many2one(
    #     'res.partner.bank', 'Bank Account Number',
    #     domain="[('partner_id', '=', address_home_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    #     groups="hr.group_hr_user",
    #     tracking=True,
    #     help='Employee bank account to pay salaries')
    # permit_no = fields.Char('Work Permit No', groups="hr.group_hr_user", tracking=True)
    # visa_no = fields.Char('Visa No', groups="hr.group_hr_user", tracking=True)
    # visa_expire = fields.Date('Visa Expiration Date', groups="hr.group_hr_user", tracking=True)
    # work_permit_expiration_date = fields.Date('Work Permit Expiration Date', groups="hr.group_hr_user", tracking=True)
    # has_work_permit = fields.Binary(string="Work Permit", groups="hr.group_hr_user", tracking=True)
    # work_permit_scheduled_activity = fields.Boolean(default=False, groups="hr.group_hr_user")
    # work_permit_name = fields.Char('work_permit_name', compute='_compute_work_permit_name')
    # additional_note = fields.Text(string='Additional Note', groups="hr.group_hr_user", tracking=True)
    # certificate = fields.Selection([
    #     ('graduate', 'Graduate'),
    #     ('bachelor', 'Bachelor'),
    #     ('master', 'Master'),
    #     ('doctor', 'Doctor'),
    #     ('other', 'Other'),
    # ], 'Certificate Level', default='other', groups="hr.group_hr_user", tracking=True)
    # study_field = fields.Char("Field of Study", groups="hr.group_hr_user", tracking=True)
    # study_school = fields.Char("School", groups="hr.group_hr_user", tracking=True)
    # emergency_contact = fields.Char("Contact Name", groups="hr.group_hr_user", tracking=True)
    # emergency_phone = fields.Char("Contact Phone", groups="hr.group_hr_user", tracking=True)
    # km_home_work = fields.Integer(string="Home-Work Distance", groups="hr.group_hr_user", tracking=True)

    # job_id = fields.Many2one(tracking=True)
    # phone = fields.Char(related='address_home_id.phone', related_sudo=False, readonly=False, string="Private Phone", groups="hr.group_hr_user")
    # # employee in company
    # child_ids = fields.One2many('hr.employee', 'parent_id', string='Direct subordinates')
    category_ids = fields.Many2many(
        'hr.employee.category', 'fls_employee_category_rel',
        'emp_id', 'category_id', groups="hr.group_hr_user",
        string='Tags')
    # # misc
    # notes = fields.Text('Notes', groups="hr.group_hr_user")
    # color = fields.Integer('Color Index', default=0)
    # barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user", copy=False)
    # pin = fields.Char(string="PIN", groups="hr.group_hr_user", copy=False,
    #     help="PIN used to Check In/Out in the Kiosk Mode of the Attendance application (if enabled in Configuration) and to change the cashier in the Point of Sale application.")
    # departure_reason_id = fields.Many2one("hr.departure.reason", string="Departure Reason", groups="hr.group_hr_user",
    #                                       copy=False, tracking=True, ondelete='restrict')
    # departure_description = fields.Html(string="Additional Information", groups="hr.group_hr_user", copy=False, tracking=True)
    # departure_date = fields.Date(string="Departure Date", groups="hr.group_hr_user", copy=False, tracking=True)
    # message_main_attachment_id = fields.Many2one(groups="hr.group_hr_user")
    # id_card = fields.Binary(string="ID Card Copy", groups="hr.group_hr_user")
    # driving_license = fields.Binary(string="Driving License", groups="hr.group_hr_user")
    # currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)

    # signed_document = fields.Many2many(readonly=True)
    # address_home_complete = fields.Char(readonly=True)  
    # country_name = fields.Char(readonly=True)

    @api.model
    def _get_fields(self):
        return ','.join('emp.%s' % name for name, field in self._fields.items() if field.store and field.type not in ['many2many', 'one2many', 'binary'])


    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT
                %s
            FROM 
                hr_employee emp
        )""" % (self._table, self._get_fields()))
    # def init(self):
    #     tools.drop_view_if_exists(self.env.cr, self._table)
    #     self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
    #         SELECT
    #             %s
    #         FROM 
    #             hr_employee emp
    #         LEFT JOIN 
    #             hr_employee_public emp_public ON emp.id = emp_public.id
    #     )""" % (self._table, self._get_fields()))


        """SELECT
 *
;"""
