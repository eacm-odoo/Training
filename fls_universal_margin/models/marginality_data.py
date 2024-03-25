from odoo import models, fields

class MarginalityData(models.Model): 
    _name = 'marginality.data'
    _description = 'Marginality Data'
    

    date = fields.Date(string='Date')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    category = fields.Char(string='Category') #AAL field name = category
    financial_account_id = fields.Many2one('account.account', string='Financial Account')
    journal_item_id = fields.Many2one('account.move.line', string='Journal Item')
    company_id = fields.Many2one('res.company', string='Company')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure') #AAL field name = product_uom_id
    quantity = fields.Float(string='Quantity') #AAL field name = unit_amount
    product_id = fields.Many2one('product.product', string='Product') #AAL field name = product_id
    so_item_id = fields.Many2one('sale.order.line', string='SO Item') # AI.SOItem
    so_item_policy_id = fields.Many2one('sale.order.line', string='SO Item Policy') # AI.SOItem.ServiceInvoicingPolicy (Timesheet, Manual, Fixed Price, etc.)
    partner_id = fields.Many2one('res.partner', string='Partner') #AAL field name = partner_id
    employee_id = fields.Many2one('hr.employee', string='Employee') #AAL field name = employee_id
    time_type = fields.Char(string='Time Type') #AAL field name = time_type selection
    adjusted = fields.Boolean(string='Adjusted') #AI.is_adjusted boolean
    multiplier = fields.Float(string='Multiplier') #AI.x_studio_multiplier # TODO: switch from studio to regular field
    resource_manager_id = fields.Many2one('hr.employee', string='Resource Manager') #AL: timesheet_manager_id
    employee_company_id = fields.Many2one('res.company', string='Employee Company') #AL: company_id
    employee_job_position_id = fields.Many2one('hr.job', string='Employee Job Position') #AL: job_id
    employee_work_country_id = fields.Many2one('res.country', string='Employee Work Country') #AL: work_country_id
    employee_fls_geo_id = fields.Many2one('fls.geo', string='Employee FLS GEO') #AL: fls_geo_id
    project_id = fields.Many2one('project.project', string='Project') #AAL field name = project_id
    project_manager_id = fields.Many2one('hr.employee', string='Project Manager') #AL: project_manager_id
    salesperson_id = fields.Many2one('res.users', string='Salesperson') #AAL field name = user_id
    operation_manager_id = fields.Many2one('hr.employee', string='Operation Manager') #AL: operation_manager_id # TODO: switch from studio to regular field
    entry_type = fields.Selection([
        ('Analytic Revenue', 'analytic_revenue'),
        ('Analytic Cost', 'analytic_cost'),
        ('Actual Revenue', 'actual_revenue'),
        ('Actual Cost', 'actual_cost')], 
        string='Entry Type') #AAL field name = entry_type
    status = fields.Selection([('Draft', 'draft'), ('In Approval', 'in_approval'), ('Approved', 'approved'), ('Posted', 'posted')], string='Status') #AAL field name = status
    currency_id = fields.Many2one('res.currency', string='Currency') #AAL field name = currency_id
    amount_currency = fields.Float(string='Amount Currency') #AAL field name = amount_currency
    amount_usd = fields.Float(string='Amount USD') #AAL field name = amount_usd


    def initialize_data(self, date_from, date_to):
        self.ensure_one()
        return 
    

    # Date
    # AnalyticAccount
    # Category
    # FinancialAccount
    # JournalItem
    # Company
    # UnitOfMeasure
    # Quantity

    # Product
    # SOItem
    # SOItemPolicy
    # Partner
    # Employee
    # TimeType

    # Adjusted,
    # Multiplier
    # ResourceManager
    # EmployeeCompany
    # EmployeeJobPosition
    # EmployeeWorkCountry
    # EmployeeFLSGeo
    # Project
    # ProjectManager
    # Salesperson
    # OperationManager
    # EntryType[ AnalyticRevenue, Analytic Cost, Actual Revenue, Actual Cost]
    # Status[ Draft, In Approval, Approved, Posted]
    # Currency
    # AmountCurrency
    # AmountUSD
