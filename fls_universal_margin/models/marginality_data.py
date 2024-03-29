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
        ('analytic_revenue', 'Analytic Revenue'),
        ('analytic_cost', 'Analytic Cost'),
        ('actual_revenue', 'Actual Revenue'),
        ('actual_cost', 'Actual Cost')], 
        string='Entry Type') #AAL field name = entry_type
    status = fields.Selection([('Draft', 'draft'), ('In Approval', 'in_approval'), ('Approved', 'approved'), ('Posted', 'posted')], string='Status') #AAL field name = status
    currency_id = fields.Many2one('res.currency', string='Currency') #AAL field name = currency_id
    amount_currency = fields.Float(string='Amount Currency') #AAL field name = amount_currency
    amount_usd = fields.Float(string='Amount USD') #AAL field name = amount_usd


    def initialize_data(self, date_from, date_to):
        marginality_data_between_range_ids = self.env['marginality.data'].search([('date','>',date_from), ('date','<',date_to)])

        if marginality_data_between_range_ids:
            marginality_data_between_range_ids.unlink()

        created_recs = self._generate_timesheet_data_with_labor_costs(date_from, date_to)

        return True
        
    
    def _generate_timesheet_data_with_labor_costs(self, date_from, date_to):
        self.env.cr.execute("""
            select 
                AAL.date as date,
                AAL.account_id as analytic_account_id,
                AAL.category as category,
                NULL as journal_item_id,
                NULL as financial_account_id,
                AAL.company_id as company_id,
                AAL.product_uom_id as uom_id,
                AAL.unit_amount as quantity,
                AAL.product_id as product_id,
                AAL.so_line as so_item_id,
                AAL.sol_product_service_invoicing_policy as so_item_policy_id,
                AAL.partner_id as partner_id,
                AAL.employee_id as employee_id,
                AAL.time_type as time_type,
                AAL.is_adjusted as adjusted,
                AAL.multiplier as multiplier,
                EH.timesheet_manager_id as resource_manager_id,
                EH.company_id as employee_company_id,
                EH.job_id as employee_job_position_id,
                EH.work_country_id as employee_work_country_id,
                EH.fls_geo_id as employee_fls_geo_id,
                AAL.project_id as project_id,
                AH.project_manager_id as project_manager_id,
                AH.salesperson_id as salesperson_id,
                AH.operating_director_id as operation_manager_id,
                'analytic_cost' as entry_type,
                NULL as status,
                AAL.currency_id as currency_id,
                AAL.amount as amount_currency,
                AAL.cost_usd as amount_usd
            from account_analytic_line AAL
            left join hr_employee_margin EH
                on
                    EH.date=AAL.Date AND 
                    EH.employee_id=AAL.employee_id
            left join analytic_account_history AH
                on 
                    AH.date=AAL.date AND 
                    AH.analytic_account_id=AAL.account_id
            where 
                AAL.date > '{date_from}' and AAL.date < '{date_to}' and
                AAL.time_type = 'regular'
            ;
            """.format(date_from = date_from.strftime('%m/%d/%Y'), date_to = date_to.strftime('%m/%d/%Y')))

        marginality_data_vals = self.env.cr.dictfetchall()
        marginality_data_recs = self.env['marginality.data'].create(marginality_data_vals)

        return marginality_data_recs
