from odoo import models
from datetime import datetime, timedelta

import re


class HrEmployeeMarginCustomHandler(models.AbstractModel):
    _name = 'hr.employee.margin.report.handler'
    _inherit = 'account.report.custom.handler'
    _description = 'Employee Margin Report Custom Handler'


    def _custom_options_initializer(self, report, options, previous_options=None):
        """ To be overridden to add report-specific _init_options... code to the report. """
        options['unfold_all'] = self._context.get('print_mode')
        if report.root_report_id and not hasattr(report, '_init_options_custom'):
            report.root_report_id._init_options_custom(options, previous_options)

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals):
        lines = []
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
        return lines
    
    def _query_employee_margin(self, field=False, id=False):
        where_clause = ""
        if field and id:
            where_clause = f"""WHERE hr_employee.{field} = {id}"""
        elif field and not id:
            where_clause = f"""WHERE hr_employee.{field} is null"""
        self._cr.execute(f"""
            WITH hr_employee_margin_info AS (
                SELECT 
                    hr_employee_margin.employee_id,
                    hr_employee_margin.date,
                    hr_employee_margin.job_id,
                    hr_employee_margin.fls_geo_id,
                    hr_employee_margin.timesheet_manager_id,
                    hr_employee_margin.work_country_id,
                    hr_employee_margin.company_id,
                    hr_employee_margin.revenue,
                    hr_employee_margin.cost
                FROM hr_employee_margin
            )
            SELECT
                hr_employee.name,
                hr_employee.id,
                hr_employee.fls_geo_id,
                hr_employee.timesheet_manager_id,
                hr_employee.work_country_id,
                JSON_AGG(hr_employee_margin_info.*)                             AS margins
            FROM hr_employee_margin_info
            INNER JOIN hr_employee
                ON hr_employee.id = hr_employee_margin_info.employee_id
            {where_clause}
            GROUP BY name, id, hr_employee.fls_geo_id, hr_employee.timesheet_manager_id, hr_employee.work_country_id
        """)

        employees = self._cr.dictfetchall()
        return employees

    def _report_expand_unfoldable_line_employee_margin_by_group_report(self, line_dict_id, groupby, options, progress, offset, unfold_all_batch_data):
        lines = []
        margins_by_employee = self._query_employee_margin()
        if groupby:
            groupby_ids = list(set(map(lambda e: e[groupby], margins_by_employee)))
            model_name = line_dict_id.replace("~","")
            groups = self.env[model_name].browse([id for id in groupby_ids if isinstance(id, int)])
            for groupby_id in groupby_ids:
                group = groups.filtered(lambda rec: rec.id == groupby_id)
                group_name = "N/A"
                group_id = 0
                if len(group) == 1:
                    group_name = group.name
                    group_id = group.id
                line_id = self.env['account.report']._get_generic_line_id(model_name, group.id, parent_line_id=line_dict_id)
                lines.append({
                    'id': line_id,
                    'name': group_name,
                    'search_key': group_name,
                    'parent_id': line_dict_id,
                    'level': 1,
                    'columns': [],
                    'groupby': f"""{groupby},{group_id}""",
                    'unfoldable': True,
                    'unfolded': True,
                    'expand_function': '_report_expand_unfoldable_line_employee_margin_report',
                    'colspan': len(options['columns']) + 1
                })
        return {
            'lines': lines
        }
    
    def _report_expand_unfoldable_line_employee_margin_report(self, line_dict_id, groupby, options, progress, offset, unfold_all_batch_data):
        lines = []
        filters = [False, False]
        if groupby:
            filters = groupby.split(',')
        margins_by_employee = self._query_employee_margin(filters[0], int(filters[1]))
        for employee in margins_by_employee:
            employee['margins'].sort(key = lambda margin: margin['date'], reverse=True)
            line_id = self.env['account.report']._get_generic_line_id('hr.employee.margin', employee['id'], parent_line_id=line_dict_id)
            lines.append({
                'id': line_id,
                'name': employee['name'],
                'parent_id': line_dict_id,
                'search_key': employee['name'],
                'columns': self._get_columns(employee, options),
                'level': 2,
                'unfoldable': False,
                'unfolded': False,
            })

        return {
            'lines': lines
        }        

    def _get_columns(self, employee, options):
        columns = options['columns']
        columns_values = []
        for column in columns:
            filters = re.findall("'([^']*)'", column['column_group_key'])
            date_range = (datetime.strptime(filters[3], '%Y-%m-%d'), datetime.strptime(filters[5], '%Y-%m-%d'))
            date_from = date_range[0]
            date_to = date_range[1] + timedelta(days=1)
            last_margin = self._get_closest_margin(employee['margins'], date_to)
            first_margin = self._get_closest_margin(employee['margins'], date_from)
            formatted_value = value = 0
            cost = last_margin['cost'] - first_margin['cost']
            revenue = last_margin['revenue'] - first_margin['revenue']
            margin = revenue + cost
            margin_percentage = 0.00
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
    
    def _get_closest_margin(self, sorted_margins, deadline, last_margin=False):
        for margin in sorted_margins:
            m_date = datetime.strptime(margin['date'], '%Y-%m-%d')
            if m_date < deadline:
                return margin
        return {'cost': 0, 'revenue': 0}
