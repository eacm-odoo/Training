from odoo import models
from datetime import datetime, timedelta

import re


class HrEmployeeMarginCustomHandler(models.AbstractModel):
    _name = 'hr.employee.margin.report.handler'
    _inherit = 'account.report.custom.handler'
    _description = 'Employee Margin Report Custom Handler'

    def _query_employee_history_fls_geo(self):
        self._cr.execute(f"""
            SELECT
                ARRAY_AGG(hr_employee_margin.fls_geo_id)                                                AS fls_geo_ids
            FROM hr_employee_margin
        """)
        res = self._cr.dictfetchall()
        fls_geo_ids = res[0]['fls_geo_ids'] if res and res[0].get('fls_geo_ids', {}) else {}
        res = list(set(fls_geo_ids)) 
        if None in res:
            res.remove(None)
        return res
    
    def _query_employee_history_work_country(self):
        self._cr.execute(f"""
            SELECT
                ARRAY_AGG(hr_employee_margin.work_country_id)                                           AS work_country_ids
            FROM hr_employee_margin
        """)
        res = self._cr.dictfetchall()
        work_country_ids = res[0]['work_country_ids'] if res and res[0].get('work_country_ids', {}) else {}
        res = list(set(work_country_ids))
        if None in res:
            res.remove(None)
        return res
    
    def _query_employee_history_timesheet_manager(self):
        self._cr.execute(f"""
            SELECT
                ARRAY_AGG(hr_employee_margin.timesheet_manager_id)                                      AS timesheet_manager_ids
            FROM hr_employee_margin
        """)
        res = self._cr.dictfetchall()
        timesheet_manager_ids = res[0]['timesheet_manager_ids'] if res and res[0].get('timesheet_manager_ids', {}) else {}
        res = list(set(timesheet_manager_ids ))
        if None in res:
            res.remove(None)
        return res
    
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
            GROUP BY hr_employee.name, hr_employee.id, hr_employee.job_id, hr_employee.fls_geo_id, hr_employee.timesheet_manager_id, hr_employee.work_country_id, hr_employee.company_id
        """)
        return self._cr.dictfetchall()
    
    def _query_timesheets(self):
        self._cr.execute(f"""
            SELECT
                hr_employee.name,
                hr_employee.id
            FROM hr_employee
            GROUP BY hr_employee.name, hr_employee.id
            ORDER BY hr_employee.name
        """)
        return self._cr.dictfetchall()
    
    def _query_invoice_lines(self):
        self._cr.execute(f"""
            SELECT
                hr_employee.name,
                hr_employee.id,
                EXTRACT(MONTH FROM account_analytic_line.date)                                         AS timesheet_month,
                EXTRACT(YEAR FROM account_analytic_line.date)                                          AS timesheet_year,
                ARRAY_AGG(sale_order_line_invoice_rel.invoice_line_id)                                 AS line_ids
            FROM hr_employee
            INNER JOIN account_analytic_line
                ON hr_employee.id = account_analytic_line.employee_id
            INNER JOIN sale_order_line
                ON sale_order_line.id = account_analytic_line.so_line
            INNER JOIN sale_order_line_invoice_rel
                ON sale_order_line.id = sale_order_line_invoice_rel.order_line_id
            GROUP BY hr_employee.id, hr_employee.name, timesheet_year, timesheet_month
        """)
        res = self._cr.dictfetchall()
        return res
    
    def _query_employee_margin(self):
        self._cr.execute(f"""
            WITH hr_employee_margin_info AS (
                SELECT 
                    hr_employee_margin.employee_id,
                    hr_employee_margin.date,
                    hr_employee_margin.job_id,
                    hr_employee_margin.fls_geo_id,
                    hr_employee_margin.timesheet_manager_id,
                    hr_employee_margin.work_country_id,
                    hr_employee_margin.company_id
                FROM hr_employee_margin
            )
            SELECT
                hr_employee.name,
                hr_employee.id,
                JSON_AGG(hr_employee_margin_info.*)                                 AS margins,
                array_agg(hr_employee_margin_info.fls_geo_id)                       AS fls_geo_id, 
                array_agg(hr_employee_margin_info.timesheet_manager_id)             AS timesheet_manager_id, 
                array_agg(hr_employee_margin_info.work_country_id)                  AS work_country_id
            FROM hr_employee_margin_info
            INNER JOIN hr_employee
                ON hr_employee.id = hr_employee_margin_info.employee_id
            GROUP BY name, id, hr_employee.fls_geo_id, hr_employee.timesheet_manager_id, hr_employee.work_country_id
        """)
        margins_by_employee = {}
        employees = self._cr.dictfetchall()
        for employee in employees:
            employee['margins'].sort(key = lambda margin: margin['date'], reverse=True)
            margins_by_employee[employee['id']] = {
                'margins': employee['margins'],
                'fls_geo_id': employee['fls_geo_id'],
                'timesheet_manager_id': employee['timesheet_manager_id'],
                'work_country_id': employee['work_country_id'],
            }
        return margins_by_employee
    
    def _custom_options_initializer(self, report, options, previous_options=None):
        """ To be overridden to add report-specific _init_options... code to the report. """
        options['unfold_all'] = self._context.get('print_mode')
        options['fls_geo_id'] = self._query_employee_history_fls_geo()
        options['work_country_id'] = self._query_employee_history_work_country()
        options['timesheet_manager_id'] = self._query_employee_history_timesheet_manager()
        if report.root_report_id and not hasattr(report, '_init_options_custom'):
            report.root_report_id._init_options_custom(options, previous_options)

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals):
        lines = []
        options['employees'] = options['employees'] if 'employees' in options else self.compile_employee_data()
        line_id = self.env['account.report']._get_generic_line_id('hr.employee', 0)
        unfold_all = options.get('unfold_all', False)
        lines.append((0, {
            'id': line_id,
            'name': "Employee",
            'level': 0,
            'columns': [],
            'unfoldable': True,
            'unfolded': unfold_all,
            'page_break': False,
            'expand_function': '_report_expand_unfoldable_line_employee_margin_report',
            'colspan': len(options['columns']) + 1
        }))
        line_id = self.env['account.report']._get_generic_line_id('fls.geo', 0)
        lines.append((0, {
            'id': line_id,
            'name': "FLS GEO",
            'level': 0,
            'columns': [],
            'groupby': 'fls_geo_id',
            'unfoldable': True,
            'unfolded': unfold_all,
            'page_break': True,
            'expand_function': '_report_expand_unfoldable_line_employee_margin_by_group_report',
            'colspan': len(options['columns']) + 1
        }))
        line_id = self.env['account.report']._get_generic_line_id('res.users', 0)
        lines.append((0, {
            'id': line_id,
            'name': "Timesheet Approver (RM)",
            'level': 0,
            'columns': [],
            'groupby': 'timesheet_manager_id',
            'unfoldable': True,
            'unfolded': unfold_all,
            'page_break': True,
            'expand_function': '_report_expand_unfoldable_line_employee_margin_by_group_report',
            'colspan': len(options['columns']) + 1
        }))
        line_id = self.env['account.report']._get_generic_line_id('res.country', 0)
        lines.append((0, {
            'id': line_id,
            'name': "Work Country",
            'level': 0,
            'columns': [],
            'groupby': 'work_country_id',
            'unfoldable': True,
            'unfolded': unfold_all,
            'page_break': True,
            'expand_function': '_report_expand_unfoldable_line_employee_margin_by_group_report',
            'colspan': len(options['columns']) + 1
        }))
        # del options['employees']
        return lines

    def _report_expand_unfoldable_line_employee_margin_by_group_report(self, line_dict_id, groupby, options, progress, offset, unfold_all_batch_data):
        lines = []
        unfold_all = options.get('unfold_all', False)
        if groupby:
            model_name = line_dict_id.replace("~","")
            groups = self.env[model_name].browse(options[groupby]).sorted(lambda rec: rec.name)
            for group in groups:
                line_id = self.env['account.report']._get_generic_line_id(model_name, group.id, parent_line_id=line_dict_id)
                lines.append({
                    'id': line_id,
                    'name': group.name,
                    'search_key': group.name,
                    'parent_id': line_dict_id,
                    'level': 1,
                    'columns': [],
                    'groupby': f"""{groupby},{group.id}""",
                    'unfoldable': True,
                    'unfolded': unfold_all,
                    'expand_function': '_report_expand_unfoldable_line_employee_margin_report',
                    'colspan': len(options['columns']) + 1
                })
            line_id = self.env['account.report']._get_generic_line_id(model_name, 0, parent_line_id=line_dict_id)
            lines.append({
                'id': line_id,
                'name': "N/A",
                'search_key': "N/A",
                'parent_id': line_dict_id,
                'level': 1,
                'columns': [],
                'groupby': f"""{groupby},0""",
                'unfoldable': True,
                'unfolded': unfold_all,
                'expand_function': '_report_expand_unfoldable_line_employee_margin_report',
                'colspan': len(options['columns']) + 1
            })
        return {
            'lines': lines
        }
    
    def _report_expand_unfoldable_line_employee_margin_report(self, line_dict_id, groupby, options, progress, offset, unfold_all_batch_data):
        lines = []
        margins_by_employee = self._query_employee_margin()
        employees = options['employees']

        def group_by_function(employee):
            if groupby:
                field_filter = groupby.split(",")
                field_name, field_value = field_filter[0], int(field_filter[1]) or None
                group_ids = margins_by_employee.get(employee['id'], {}).get(field_name, [])
                return field_value in group_ids
            return False

        filtered_employees = list(filter(group_by_function, employees)) if groupby else employees
        for employee in filtered_employees:
            margin_data = margins_by_employee.get(employee['id'], {})
            line_id = self.env['account.report']._get_generic_line_id('hr.employee.margin', employee['id'], parent_line_id=line_dict_id)
            lines.append({
                'id': line_id,
                'name': employee['name'],
                'parent_id': line_dict_id,
                'search_key': employee['name'],
                'columns': self._get_columns(employee, margin_data.get('margins', []), options, groupby),
                'level': 2,
                'unfoldable': False,
                'unfolded': False,
            })

        return {
            'lines': lines
        }        

    def compile_employee_data(self, line_dict_id=None, group_by=None):
        employees = self._query_timesheets()
        usd_currency = self.env['res.currency'].search([('name','=','USD')], limit=1) 
        margins_by_employee = self._query_employee_margin()
        # pre-fetch all sale order lines that are not delivered timesheet
        sol_ids = self.env['sale.order.line'].search([('product_id.service_policy','!=','delivered_timesheet')])
        sol_ids = sol_ids.filtered(lambda l: l.product_id.service_policy != 'delivered_timesheet')

        def group_by_function(employee):
            field_filter = group_by.split(",")
            field_name, field_value = field_filter[0], int(field_filter[1]) or None
            group_ids = margins_by_employee.get(employee['id'], {}).get(field_name, [])
            return field_value in group_ids
            

        filtered_employees = list(filter(group_by_function, employees)) if group_by else employees
        for employee in filtered_employees:
            employee['records'] = []
            hr_employee = self.env['hr.employee'].sudo().browse([employee['id']])
            if hr_employee.timesheet_ids:
                for aal in hr_employee.timesheet_ids:
                    # aal = self.env['account.analytic.line'].browse([rec['id']])
                    employee['records'].append({
                        'id': aal.id,
                        'employee_id': aal.employee_id.id,
                        'so_line': aal.so_line.id,
                        'date': aal.date,
                        'timesheet_month': aal.date.month,
                        'timesheet_year': aal.date.year,
                        'cost': aal.cost_usd,
                        'revenue': aal.sudo()._compute_line_revenue_usd(aal.date.month, aal.date.year, aal.employee_id.id),
                    })
        return filtered_employees

    def _get_columns(self, employee_timesheets, employee_margins, options, groupby):
        columns = options['columns']
        columns_values = []
        for column in columns:
            filters = re.findall("'([^']*)'", column['column_group_key'])
            date_from = datetime.strptime(filters[3], '%Y-%m-%d')
            date_to = datetime.strptime(filters[5], '%Y-%m-%d')
            formatted_value = value = cost = revenue = 0
            date_ranges = [[date_from, date_to]]
            if groupby:
                field_filter = groupby.split(",")
                field_name, field_value = field_filter[0], int(field_filter[1]) or None
                date_ranges = self._get_groupby_date_ranges(employee_margins, field_name, field_value, date_from, date_to)
            for rec in employee_timesheets['records']:
                rec_date = datetime.strptime(rec['date'], '%Y-%m-%d')
                if any(date_range[0] <= rec_date and date_range[1] >= rec_date for date_range in date_ranges):
                    cost += rec['cost']
                    revenue += rec['revenue']
            margin = revenue + cost
            margin_percentage = 0.00
            cost = float(cost)
            margin = float(margin)
            margin_percentage = float(margin_percentage)
            if column['name'] == 'Cost':
                formatted_value = '$\xa0{0:,.2f}'.format(cost)
                value = cost
            elif column['name'] == 'Revenue':
                formatted_value = '$\xa0{0:,.2f}'.format(revenue)
                value = revenue
            elif column['name'] == 'Margin':
                formatted_value = '$\xa0{0:,.2f}'.format(margin)
                value = margin
            elif column['name'] == 'Margin %':
                if revenue != 0:
                    margin_percentage = margin/revenue*100
                formatted_value = '{0:,.2f}\xa0%'.format(margin_percentage)
                value = margin_percentage
            columns_values.append({
                'name': formatted_value,
                'no_format': value,
                'class': 'number',
            })
        return columns_values
    
    def _get_groupby_date_ranges(self, sorted_margins, field, value, date_from, date_to):
        date_ranges = []
        prev_date = date_to
        for margin in sorted_margins:
            m_date = datetime.strptime(margin['date'], '%Y-%m-%d')
            if m_date <= date_to and m_date >= date_from:
                if margin[field] == value:
                    date_ranges.append([m_date, prev_date])
                prev_date = m_date
            elif m_date < date_from and margin[field] == value:
                date_ranges.append([date_from, prev_date])
                break
            elif m_date < date_from:
                break
        return date_ranges
