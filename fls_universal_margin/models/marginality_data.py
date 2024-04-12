from odoo import models, fields
import logging
import time

_logger = logging.getLogger(__name__)


SQL_QUERY_FUNCTIONS = [
    '_generate_timesheet_data_with_labor_costs', 
    '_generate_timesheet_data_with_invoiced_revenue', 
    '_generate_data_for_revenue_on_timesheet_not_hour', 
    '_generate_data_for_fixed_price_revenue_invoice', 
    '_generate_timesheet_data_with_non_invoiced_revenue', 
    '_generate_data_based_on_non_invoiced_delivered_quantities', 
    '_generate_data_for_non_timesheet_revenue_and_cost', 
]
def timeis(func): 
        '''Decorator that reports the execution time.'''
        def wrap(*args, **kwargs): 
            start = time.time() 
            _logger.log(logging.INFO, f'Starting: {func.__name__}')
            result = func(*args, **kwargs) 
            _logger.log(logging.INFO, f'finished: {func.__name__} in : {time.time()- start}')
            return result 
        return wrap 
        
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
    so_item_policy_id = fields.Selection(string='Service Item Policy', selection=[
        ('ordered_prepaid','Prepaid/Fixed Price'), 
        ('delivered_timesheet','Based on Timesheets'), 
        ('delivered_milestones','Based on Milestones'), 
        ('delivered_manual','Based on Delivered Quantity (Manual)')])
    partner_id = fields.Many2one('res.partner', string='Partner') #AAL field name = partner_id
    employee_id = fields.Many2one('hr.employee', string='Employee') #AAL field name = employee_id
    time_type = fields.Char(string='Time Type') #AAL field name = time_type selection
    adjusted = fields.Boolean(string='Adjusted') #AI.is_adjusted boolean
    multiplier = fields.Float(string='Multiplier') #AI.x_studio_multiplier
    resource_manager_id = fields.Many2one('res.users', string='Resource Manager') #AL: timesheet_manager_id
    employee_company_id = fields.Many2one('res.company', string='Employee Company') #AL: company_id
    employee_job_position_id = fields.Many2one('hr.job', string='Employee Job Position') #AL: job_id
    employee_work_country_id = fields.Many2one('res.country', string='Employee Work Country') #AL: work_country_id
    employee_fls_geo_id = fields.Many2one('fls.geo', string='Employee FLS GEO') #AL: fls_geo_id
    project_id = fields.Many2one('project.project', string='Project') #AAL field name = project_id
    project_manager_id = fields.Many2one('hr.employee', string='Project Manager') #AL: project_manager_id
    salesperson_id = fields.Many2one('res.users', string='Salesperson') #AAL field name = user_id
    operation_manager_id = fields.Many2one('hr.employee', string='Operation Manager') #AL: operation_manager_id
    entry_type = fields.Selection([
        ('analytic_revenue', 'Analytic Revenue'),
        ('analytic_cost', 'Analytic Cost'),
        ('actual_revenue', 'Actual Revenue'),
        ('actual_cost', 'Actual Cost')], 
        string='Entry Type') #AAL field name = entry_type
    status = fields.Selection([
        ('draft', 'Draft'), 
        ('in_approval', 'In Approval'), 
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'), 
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
        ('rejected', 'Rejected')], string='Status') #AAL field name = status
    currency_id = fields.Many2one(ondelete='cascade', comodel_name='res.currency', string='Currency') #AAL field name = currency_id
    amount_currency = fields.Float(string='Amount Currency') #AAL field name = amount_currency
    amount_usd = fields.Float(string='Amount USD') #AAL field name = amount_usd


    @timeis
    def initialize_data(self, date_from, date_to):
        marginality_data_between_range_ids = self.env['marginality.data'].search([('date','>',date_from), ('date','<',date_to)])

        # self.with_user(33).with_company(1).env['documents.document'].search([])

        if marginality_data_between_range_ids:
            marginality_data_between_range_ids.unlink()

        vals = []
        for query in SQL_QUERY_FUNCTIONS:
            try:
                new_vals = getattr(self, query)(date_from, date_to)
                _logger.error(f'VALS: {query} generated {len(new_vals)} rows')
                vals += new_vals
            except Exception as e:
                _logger.error(f'ERROR: FLS UNIVERSAL MARGIN REPORT - {query}\n{e}')
                continue

        recs = self.env['marginality.data'].create(vals)
        return recs
        
    # Step 2
    @timeis
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
                AAL.date > '{date_from}' and AAL.date < '{date_to}' 
                and AAL.time_type = 'regular'
            ;
            """.format(date_from = date_from.strftime('%m/%d/%Y'), date_to = date_to.strftime('%m/%d/%Y')))

        marginality_data_vals = self.env.cr.dictfetchall()
        # marginality_data_recs = self.env['marginality.data'].create(marginality_data_vals)
        # return marginality_data_recs
        return marginality_data_vals

    # Step 3
    @timeis
    def _generate_timesheet_data_with_invoiced_revenue(self, date_from, date_to):
        self.env.cr.execute("""
            select 
                JI.date as date,
                (select POL.analytic_account from purchase_order_line POL where POL.id = JI.purchase_line_id) as analytic_account_id,
                AAL.category as category,
                JI.account_id as financial_account_id,
                JI.id as journal_item_id,
                JI.company_id as company_id,
                AAL.product_uom_id as uom_id,
                AAL.unit_amount as quantity,
                AAL.product_id as product_id,
                AAL.so_line as so_item_id,
                AAL.sol_product_service_invoicing_policy as so_item_policy_id,
                JI.partner_id as partner_id,
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
                'actual_revenue' as entry_type,
                NULL as status,
                JI.currency_id as currency_id,
                (JI.price_unit * JI.quantity)/AAL.unit_amount as amount_currency,
                ((JI.price_unit * JI.quantity)/AAL.unit_amount) * AAL.exchange_rate_usd as amount_usd
            from account_analytic_line AAL
            left join hr_employee_margin EH
                on
                    EH.date=AAL.Date AND 
                    EH.employee_id=AAL.employee_id
            left join analytic_account_history AH
                on 
                    AH.date=AAL.date AND 
                    AH.analytic_account_id=AAL.account_id
            left join account_move_line AML
                on 
                    AAL.move_line_id=AML.id 
            FULL OUTER join account_move_line JI
                on 
                    AAL.move_line_id=JI.id 
            where 
                AAL.date > '{date_from}' and AAL.date < '{date_to}' 
                and JI.date > '{date_from}' and JI.date < '{date_to}' 
                and AAL.time_type = 'regular' 
                and AAL.sol_product_service_invoicing_policy = 'delivered_timesheet'
            ;
            """.format(date_from = date_from.strftime('%m/%d/%Y'), date_to = date_to.strftime('%m/%d/%Y')))

        marginality_data_vals = self.env.cr.dictfetchall()
        # marginality_data_recs = self.env['marginality.data'].create(marginality_data_vals)
        # return marginality_data_recs
        return marginality_data_vals

    # step 4
    @timeis
    def _generate_data_for_revenue_on_timesheet_not_hour(self, date_from, date_to):
        self.env.cr.execute("""
            select
                JI.date as date,
                (select POL.analytic_account from purchase_order_line POL where POL.id = JI.purchase_line_id) as analytic_account_id,
                AIG.category as category,
                JI.account_id as financial_account_id,
                JI.id as journal_item_id,
                JI.company_id as company_id,
                AIG.uom_id as uom_id,
                AIG.quantity as quantity,
                AIG.product_id as product_id,
                AIG.so_item_id as so_item_id,
                AIG.so_item_policy_id as so_item_policy_id,
                JI.partner_id as partner_id,
                AIG.employee_id as employee_id,
                NULL as time_type,
                NULL as adjusted,
                null as multiplier,
                EH.timesheet_manager_id as resource_manager_id,
                EH.company_id as employee_company_id,
                EH.job_id as employee_job_position_id,
                EH.work_country_id as employee_work_country_id,
                EH.fls_geo_id as employee_fls_geo_id,
                AIG.project_id as project_id,
                AH.project_manager_id as project_manager_id,
                AH.salesperson_id as salesperson_id,
                AH.operating_director_id as operation_manager_id,
                'actual_revenue' as entry_type,
                (select AM.state from account_move AM where AM.id=JI.move_id) as status,
                JI.currency_id as currency_id,
                JI.price_unit / JI.quantity as amount_currency,
                ((JI.price_unit / JI.quantity)* JI.exchange_rate_company_currency * JI.exchange_rate_usd) as amount_usd
            from 
            (
                select
                    AAL.category as category,
                    AAL.date as date,
                    AAL.product_uom_id as uom_id,
                    sum(AAL.unit_amount) as quantity,
                    AAL.product_id as product_id,
                    AAL.so_line as so_item_id,
                    AAL.sol_product_service_invoicing_policy as so_item_policy_id,
                    AAL.employee_id  as employee_id,
                    AAL.project_id as project_id,

                    AAL.timesheet_invoice_id as timesheet_invoice_id
                from account_analytic_line as AAL
                where 
                    AAL.time_type = 'regular' 
                    and AAl.sol_product_service_invoicing_policy = 'delivered_manual'  
                group by 
                    DATE_TRUNC('month',AAL.date), 
                    AAL.date, 
                    AAL.product_uom_id,
                    AAL.category, 
                    AAL.unit_amount,AAL.product_id,
                    AAL.so_line,
                    AAL.sol_product_service_invoicing_policy,
                    AAL.employee_id,
                    AAL.project_id, 
                    AAL.timesheet_invoice_id
            ) as AIG
            left join account_move_line JI
                on 
                    AIG.timesheet_invoice_id=JI.id 
            left outer join hr_employee_margin EH
                on
                    EH.date=AIG.Date AND 
                    EH.employee_id=AIG.employee_id
            left join analytic_account_history AH
                on 
                    AH.date=AIG.date AND 
                    AH.analytic_account_id=JI.account_id
            where
                AIG.date > '{date_from}' and AIG.date < '{date_to}' and
                JI.date > '{date_from}' and JI.date < '{date_to}' and
                JI.parent_state != 'cancel'
            ;
        """.format(date_from = date_from.strftime('%m/%d/%Y'), date_to = date_to.strftime('%m/%d/%Y')))

        marginality_data_vals = self.env.cr.dictfetchall()
        # marginality_data_recs = self.env['marginality.data'].create(marginality_data_vals)
        # return marginality_data_recs
        return marginality_data_vals


    # step 5: Produce data entries for revenue invoiced on fixed price assignments.
    @timeis
    def _generate_data_for_fixed_price_revenue_invoice(self, date_from, date_to):
        self.env.cr.execute("""
            select
                JI.date as date,
                (select POL.analytic_account from purchase_order_line POL where POL.id = JI.purchase_line_id) as analytic_account_id,
                AIG.category as category,
                JI.account_id as financial_account_id,
                JI.id as journal_item_id,
                JI.company_id as company_id,
                AIG.uom_id as uom_id,
                AIG.quantity as quantity,
                AIG.product_id as product_id,
                AIG.so_item_id as so_item_id,
                AIG.so_item_policy_id as so_item_policy_id,
                JI.partner_id as partner_id,
                AIG.employee_id as employee_id,
                NULL as time_type,
                NULL as adjusted,
                null as multiplier,
                EH.timesheet_manager_id as resource_manager_id,
                EH.company_id as employee_company_id,
                EH.job_id as employee_job_position_id,
                EH.work_country_id as employee_work_country_id,
                EH.fls_geo_id as employee_fls_geo_id,
                AIG.project_id as project_id,
                AH.project_manager_id as project_manager_id,
                AH.salesperson_id as salesperson_id,
                AH.operating_director_id as operation_manager_id,
                'actual_revenue' as entry_type,
                (select AM.state from account_move AM where AM.id=JI.move_id) as status,
                JI.currency_id as currency_id,
                (JI.price_unit / (
                    (
                        select
                        count(*)
                        from account_analytic_line as AAL
                        where 
                            AAL.time_type = 'regular' 
                            and AAl.sol_product_service_invoicing_policy = 'ordered_prepaid'  
                        group by 
                            DATE_TRUNC('month',AAL.date), 
                            AAL.date, 
                            AAL.product_uom_id,
                            AAL.category, 
                            AAL.unit_amount,AAL.product_id,
                            AAL.so_line,
                            AAL.sol_product_service_invoicing_policy,
                            AAL.employee_id,
                            AAL.project_id, 
                            AAL.timesheet_invoice_id
                    )
                )) as amount_currency,
                ((JI.price_unit / (
                    (
                        select
                        count(*)
                        from account_analytic_line as AAL
                        where 
                            AAL.time_type = 'regular' 
                            and AAl.sol_product_service_invoicing_policy = 'ordered_prepaid'  
                        group by 
                            DATE_TRUNC('month',AAL.date), 
                            AAL.date, 
                            AAL.product_uom_id,
                            AAL.category, 
                            AAL.unit_amount,AAL.product_id,
                            AAL.so_line,
                            AAL.sol_product_service_invoicing_policy,
                            AAL.employee_id,
                            AAL.project_id, 
                            AAL.timesheet_invoice_id
                    )
                )) * JI.exchange_rate_company_currency * JI.exchange_rate_usd) as amount_usd
            from 
            (
                select
                    AAL.category as category,
                    AAL.date as date,
                    AAL.product_uom_id as uom_id,
                    sum(AAL.unit_amount) as quantity,
                    AAL.product_id as product_id,
                    AAL.so_line as so_item_id,
                    AAL.sol_product_service_invoicing_policy as so_item_policy_id,
                    AAL.employee_id  as employee_id,
                    AAL.project_id as project_id,
                    AAL.timesheet_invoice_id as timesheet_invoice_id
                from account_analytic_line as AAL
                where 
                    AAL.time_type = 'regular' 
                    and AAl.sol_product_service_invoicing_policy = 'ordered_prepaid'  
                group by 
                    DATE_TRUNC('month',AAL.date), 
                    AAL.date, 
                    AAL.product_uom_id,
                    AAL.category, 
                    AAL.unit_amount,AAL.product_id,
                    AAL.so_line,
                    AAL.sol_product_service_invoicing_policy,
                    AAL.employee_id,
                    AAL.project_id, 
                    AAL.timesheet_invoice_id
            ) as AIG
            left join account_move_line JI
                on 
                    AIG.timesheet_invoice_id=JI.id 
            left outer join hr_employee_margin EH
                on
                    EH.date=AIG.Date AND 
                    EH.employee_id=AIG.employee_id
            left join analytic_account_history AH
                on 
                    AH.date=AIG.date AND 
                    AH.analytic_account_id=JI.account_id
            where
                AIG.date > '{date_from}' and AIG.date < '{date_to}' and
                JI.date > '{date_from}' and JI.date < '{date_to}' and
                JI.parent_state != 'cancel'
            ;
        """.format(date_from = date_from.strftime('%m/%d/%Y'), date_to = date_to.strftime('%m/%d/%Y')))    

        marginality_data_vals = self.env.cr.dictfetchall()
        # marginality_data_recs = self.env['marginality.data'].create(marginality_data_vals)
        # return marginality_data_recs
        return marginality_data_vals


        
    # Step 6: Produce data entries for “based on timesheets” revenue not invoiced yet.
    @timeis
    def _generate_timesheet_data_with_non_invoiced_revenue(self, date_from, date_to):
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
                'analytic_revenue' as entry_type,
                NULL as status,
                SOL.currency_id as currency_id,
                (SOL.price_total * AAL.unit_amount) as amount_currency,
                (SOL.price_total * AAL.unit_amount * AAL.exchange_rate_company_currency * AAL.exchange_rate_usd) as amount_usd
            from account_analytic_line AAL
            left outer join hr_employee_margin EH
                on
                    EH.date=AAL.Date AND 
                    EH.employee_id=AAL.employee_id
            left outer join analytic_account_history AH
                on 
                    AH.date=AAL.date AND 
                    AH.analytic_account_id=AAL.account_id
            left outer join sale_order_line SOL
                on 
                    SOL.id=AAL.so_line
            where 
                AAL.date > '{date_from}' and AAL.date < '{date_to}' 
                and AAL.time_type = 'regular' 
                and AAL.sol_product_service_invoicing_policy= 'delivered_timesheet'
            ;
            """.format(date_from = date_from.strftime('%m/%d/%Y'), date_to = date_to.strftime('%m/%d/%Y')))

        marginality_data_vals = self.env.cr.dictfetchall()
        # marginality_data_recs = self.env['marginality.data'].create(marginality_data_vals)
        # return marginality_data_recs
        return marginality_data_vals

    # Step 7: Produce data entries for “based on timesheets” revenue not invoiced yet.
    @timeis
    def _generate_data_based_on_non_invoiced_delivered_quantities(self, date_from, date_to):
        self.env.cr.execute("""
            select
                JI.date as date,
                (select POL.analytic_account from purchase_order_line POL where POL.id = JI.purchase_line_id) as analytic_account_id,
                AIG.category as category,
                JI.account_id as financial_account_id,
                JI.id as journal_item_id,
                JI.company_id as company_id,
                AIG.uom_id as uom_id,
                AIG.quantity as quantity,
                AIG.product_id as product_id,
                AIG.so_item_id as so_item_id,
                AIG.so_item_policy_id as so_item_policy_id,
                JI.partner_id as partner_id,
                AIG.employee_id as employee_id,
                NULL as time_type,
                NULL as adjusted,
                null as multiplier,
                EH.timesheet_manager_id as resource_manager_id,
                EH.company_id as employee_company_id,
                EH.job_id as employee_job_position_id,
                EH.work_country_id as employee_work_country_id,
                EH.fls_geo_id as employee_fls_geo_id,
                AIG.project_id as project_id,
                AH.project_manager_id as project_manager_id,
                AH.salesperson_id as salesperson_id,
                AH.operating_director_id as operation_manager_id,
                'analytic_revenue' as entry_type,
                NULL as status,
                SOL.currency_id as currency_id,
                (SOL.price_total) as amount_currency,
                (SOL.price_total * JI.exchange_rate_company_currency * JI.exchange_rate_usd) as amount_usd
            from 
            (
                select
                    AAL.category as category,
                    AAL.date as date,
                    AAL.product_uom_id as uom_id,
                    sum(AAL.unit_amount) as quantity,
                    AAL.product_id as product_id,
                    AAL.so_line as so_item_id,
                    AAL.sol_product_service_invoicing_policy as so_item_policy_id,
                    AAL.employee_id  as employee_id,
                    AAL.project_id as project_id,
                    AAL.timesheet_invoice_id as timesheet_invoice_id
                from account_analytic_line as AAL
                where 
                    AAL.time_type = 'regular' 
                    and AAl.sol_product_service_invoicing_policy = 'delivered_manual'  
                group by 
                    DATE_TRUNC('month',AAL.date), 
                    AAL.date, 
                    AAL.product_uom_id,
                    AAL.category, 
                    AAL.unit_amount,AAL.product_id,
                    AAL.so_line,
                    AAL.sol_product_service_invoicing_policy,
                    AAL.employee_id,
                    AAL.project_id, 
                    AAL.timesheet_invoice_id
            ) as AIG
            left outer join sale_order_line SOL
                on 
                    SOL.id=AIG.so_item_id
            left join account_move_line JI
                on 
                    AIG.timesheet_invoice_id=JI.id 
            left outer join hr_employee_margin EH
                on
                    EH.date=AIG.Date AND 
                    EH.employee_id=AIG.employee_id
            left join analytic_account_history AH
                on 
                    AH.date=AIG.date AND 
                    AH.analytic_account_id=JI.account_id
            where
                AIG.date > '{date_from}' and AIG.date < '{date_to}' and
                JI.date > '{date_from}' and JI.date < '{date_to}' and
                JI.parent_state != 'cancel'
            ;
        """.format(date_from = date_from.strftime('%m/%d/%Y'), date_to = date_to.strftime('%m/%d/%Y')))

        marginality_data_vals = self.env.cr.dictfetchall()
        # marginality_data_recs = self.env['marginality.data'].create(marginality_data_vals)
        # return marginality_data_recs
        return marginality_data_vals

    # Step 8: Produce data entries for revenue and cost not related to timesheets
    @timeis
    def _generate_data_for_non_timesheet_revenue_and_cost(self, date_from, date_to):
        self.env.cr.execute("""
            select 
                JI.date as date,
                (select POL.analytic_account from purchase_order_line POL where POL.id = JI.purchase_line_id) as analytic_account_id,
                (select AM.move_type from account_move AM where AM.id=JI.move_id) as category,
                JI.account_id as financial_account_id,
                JI.id as journal_item_id,
                JI.company_id as company_id,
                JI.product_uom_id as uom_id,
                JI.quantity as quantity,
                JI.product_id as product_id,
                JI.so_item_id as so_item_id,
                (select P.invoice_policy from product_template P where JI.id=P.id) as so_item_policy_id,
                JI.partner_id as partner_id,
                (select RP.employee_id from res_partner RP where RP.id=JI.partner_id limit 1) as employee_id,
                NULL as time_type,
                NULL as adjusted,
                NULL as multiplier,
                CASE
                    WHEN (select count(RP.id) from res_partner RP where RP.id=JI.partner_id) > 0 THEN EH.timesheet_manager_id
                    ELSE NULL
                END as resource_manager_id,
                CASE
                    WHEN (select count(RP.id) from res_partner RP where RP.id=JI.partner_id) > 0 THEN EH.company_id
                    ELSE NULL
                END as employee_company_id,
                CASE
                    WHEN (select count(RP.id) from res_partner RP where RP.id=JI.partner_id) > 0 THEN EH.job_id
                    ELSE NULL
                END as employee_job_position_id,
                CASE
                    WHEN (select count(RP.id) from res_partner RP where RP.id=JI.partner_id) > 0 THEN EH.work_country_id
                    ELSE NULL
                END as employee_work_country_id,
                CASE
                    WHEN (select count(RP.id) from res_partner RP where RP.id=JI.partner_id) > 0 THEN EH.fls_geo_id
                    ELSE NULL
                END as employee_fls_geo_id,
                (select id from project_project PP where JI.so_item_id=PP.sale_line_id limit 1) as project_id,
                AH.project_manager_id as project_manager_id,
                AH.salesperson_id as salesperson_id,
                AH.operating_director_id as operation_manager_id,
                'actual_cost' as entry_type,
                (select AM.state from account_move AM where AM.id=JI.move_id) as status,
                JI.currency_id as currency_id,
                JI.price_unit * JI.quantity as amount_currency,
                ((JI.price_unit * JI.quantity) * JI.exchange_rate_usd * JI.exchange_rate_company_currency) as amount_usd
            from account_move_line JI
            left join analytic_account_history AH
                on 
                    AH.date=JI.date AND 
                    AH.analytic_account_id=(select POL.analytic_account from purchase_order_line POL where POL.id = JI.purchase_line_id)
            left join hr_employee_margin EH
                on
                    EH.date=JI.Date AND 
                    EH.employee_id=JI.fls_partner_employee_id
            where 
                JI.date > '{date_from}' and JI.date < '{date_to}' and
                JI.parent_state != 'cancel' and
                (select count(*) from account_analytic_line AAL where AAL.move_line_id=JI.id) = 0
        ;
        """.format(date_from = date_from.strftime('%m/%d/%Y'), date_to = date_to.strftime('%m/%d/%Y')))

        marginality_data_vals = self.env.cr.dictfetchall()
        # marginality_data_recs = self.env['marginality.data'].create(marginality_data_vals)
        # return marginality_data_recs
        return marginality_data_vals
