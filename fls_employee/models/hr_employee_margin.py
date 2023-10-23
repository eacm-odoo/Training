from odoo import fields, models, api

from datetime import date
from collections import Counter


class HrEmployeeMargin(models.Model):
    _name = 'hr.employee.margin'
    _description = 'Employee Margin'

    name = fields.Char()
    date = fields.Date(string='Date', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    job_id = fields.Many2one('hr.job', string='Job')
    fls_geo_id = fields.Many2one('fls.geo', string='FLS GEO')
    timesheet_manager_id = fields.Many2one('res.users', string='Timesheet Approver')
    work_country_id = fields.Many2one('res.country', string='Work Country')
    company_id = fields.Many2one('res.company', string='Company')
    revenue = fields.Float(string='Revenue', required=True)
    cost = fields.Float(string='Cost', required=True)
 
    def _query_employees(self):
        self._cr.execute(f"""
            SELECT
                hr_employee.name,
                hr_employee.id,
                hr_employee.job_id,
                hr_employee.fls_geo_id,
                hr_employee.timesheet_manager_id,
                hr_employee.work_country_id,
                hr_employee.company_id,
            FROM hr_employee
            INNER JOIN account_analytic_line
                ON hr_employee.id = account_analytic_line.employee_id
            GROUP BY hr_employee.name, hr_employee.id, hr_employee.job_id, hr_employee.fls_geo_id, hr_employee.timesheet_manager_id, hr_employee.work_country_id, hr_employee.company_id,
        """)
        return self._cr.dictfetchall()
    
    def _query_timesheets(self):
        self._cr.execute(f"""
            SELECT
                hr_employee.id,
                account_analytic_line.currency_id,
                account_analytic_line.company_id,
                account_analytic_line.date                                                          AS date,
                SUM(account_analytic_line.amount)                                                   AS cost
            FROM hr_employee
            INNER JOIN account_analytic_line
                ON hr_employee.id = account_analytic_line.employee_id
            GROUP BY hr_employee.id, account_analytic_line.currency_id, account_analytic_line.company_id, date
        """)
        return self._cr.dictfetchall()
    
    def _query_invoice_lines(self):
        self._cr.execute(f"""
            SELECT
                hr_employee.name,
                hr_employee.id,
                hr_employee.job_id,
                hr_employee.fls_geo_id,
                hr_employee.timesheet_manager_id,
                hr_employee.work_country_id,
                hr_employee.company_id,
                SUM(account_analytic_line.unit_amount)                                              AS qty,
                product_template.service_policy,
                array_agg(sale_order_line_invoice_rel.invoice_line_id)                              AS line_ids
            FROM hr_employee
            INNER JOIN account_analytic_line
                ON hr_employee.id = account_analytic_line.employee_id
            INNER JOIN sale_order_line
                ON sale_order_line.id = account_analytic_line.so_line
            INNER JOIN product_product
                ON product_product.id = sale_order_line.product_id
            INNER JOIN product_template
                ON product_template.id = product_product.product_tmpl_id
            INNER JOIN (
                SELECT
                    invoice_line_id,
                    order_line_id
                FROM sale_order_line_invoice_rel
                GROUP BY order_line_id, invoice_line_id
            ) sale_order_line_invoice_rel ON sale_order_line_invoice_rel.order_line_id = sale_order_line.id
            GROUP BY hr_employee.name, hr_employee.id, hr_employee.job_id, hr_employee.fls_geo_id, hr_employee.timesheet_manager_id, hr_employee.work_country_id, hr_employee.company_id, product_template.service_policy
        """)
        res = self._cr.dictfetchall()
        employee_revenues = {}
        for ev in res:
            ev['line_ids'] = list(set(ev.get('line_ids', [])))
            if not employee_revenues.get(ev['id'], False):
                ev['lines_by_policy'] = {ev['service_policy']: ev['line_ids']}
                employee_revenues[ev['id']] = ev
            else:
                employee_revenues[ev['id']]['lines_by_policy'][ev['service_policy']] = ev['line_ids']
                employee_revenues[ev['id']]['line_ids'] = employee_revenues[ev['id']]['line_ids'] + ev['line_ids']
        return employee_revenues
            

    def _query_last_employee_margins(self):
        self._cr.execute(f"""
            SELECT DISTINCT ON (hr_employee.id)
                hr_employee_margin.*
            FROM hr_employee
            INNER JOIN hr_employee_margin
                ON hr_employee.id = hr_employee_margin.employee_id
            ORDER BY 
                hr_employee.id,
                hr_employee_margin.date DESC
        """)
        res = self._cr.dictfetchall()
        latest_margins ={}
        for em in res:
            latest_margins[em['employee_id']] = em
            if em['job_id'] == None:
                em['job_id'] = False
            if em['fls_geo_id'] == None:
                em['fls_geo_id'] = False
            if em['timesheet_manager_id'] == None:
                em['timesheet_manager_id'] = False
            if em['work_country_id'] == None:
                em['work_country_id'] = False
            if em['company_id'] == None:
                em['company_id'] = False
        return latest_margins

    @api.model
    def calculate_employee_margin(self, initialize=False):
        employee_invoice_records = self._query_invoice_lines()
        employee_timesheet_records = self._query_timesheets()
        employees = self.env['hr.employee'].search([])
        latest_margins = self._query_last_employee_margins()
        all_line_ids = []
        margin_creations = []
        employee_count_by_line = Counter()

        for employee in employee_invoice_records.values():
            employee_count_by_line.update(employee['line_ids'])
            all_line_ids += employee['line_ids']

        all_line_ids = list(set(all_line_ids))
        all_move_lines = self.env['account.move.line'].search([('id', 'in', all_line_ids),('move_type','=','out_invoice'),('parent_state', '!=', 'cancel')])
        usd_currency = self.env['res.currency'].search([('name','=','USD')], limit=1) 

        for employee_id in employees:
            employee_data = {}
            employee = employee_invoice_records.get(employee_id.id, {})
            employee_lines = all_move_lines.filtered(lambda l: l.id in employee.get('line_ids', []))
            revenue = 0
            cost = 0
            for line in employee_lines:
                currency_conversion_rate = self.env['res.currency']._get_conversion_rate(line.currency_id,usd_currency,line.company_id,line.move_id.date.strftime("%m/%d/%y"))
                if line.id in employee['lines_by_policy'].get('delivered_timesheet', []):
                    revenue += line.price_subtotal*currency_conversion_rate
                else:
                    revenue += (line.price_subtotal*currency_conversion_rate)/employee_count_by_line[line.id]
            for timesheet in filter(lambda rec: rec['id'] == employee_id.id,employee_timesheet_records):
                from_currency = self.env['res.currency'].browse([timesheet['currency_id']])
                company = self.env['res.company'].browse([timesheet['company_id']])
                currency_conversion_rate = self.env['res.currency']._get_conversion_rate(from_currency,usd_currency,company,timesheet['date'].strftime("%m/%d/%y"))
                cost += timesheet['cost']*currency_conversion_rate
            margin_date = None
            if initialize:
                margin_date = date(2023, 1, 1)
            else:
                margin_date = date.today()
            if self.check_margin_differences(employee_id, revenue, cost, latest_margins.get(employee_id.id, False)) or initialize:
                margin_creations.append({
                    'name': '{}-{}'.format(employee_id.name,margin_date),
                    'date': margin_date,
                    'employee_id': employee_id.id,
                    'job_id': employee_id.job_id.id,
                    'fls_geo_id': employee_id.fls_geo_id.id,
                    'timesheet_manager_id': employee_id.timesheet_manager_id.id,
                    'work_country_id': employee_id.work_country_id.id,
                    'company_id': employee_id.company_id.id,
                    'revenue': revenue,
                    'cost': cost
                })
        if len(margin_creations) > 0:
            self.env['hr.employee.margin'].create(margin_creations)

    def check_margin_differences(self, employee, revenue, cost, last_margin):
        if last_margin:
            return not (
                employee.job_id.id == last_margin['job_id'] and
                employee.fls_geo_id.id == last_margin['fls_geo_id'] and
                employee.timesheet_manager_id.id == last_margin['timesheet_manager_id'] and
                employee.work_country_id.id == last_margin['work_country_id'] and
                employee.company_id.id == last_margin['company_id'] and
                revenue == last_margin['revenue'] and
                cost == last_margin['cost']
            )
        return True
