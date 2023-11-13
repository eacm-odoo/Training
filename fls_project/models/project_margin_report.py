from odoo import models, fields
from datetime import date, datetime
import re


class ProjectReport(models.Model):
    _name = "project.margin.report.handler"
    _inherit = ["account.report.custom.handler"]
    _description = "Project Margin Report Handler"
    
    def _custom_options_initializer(self, report, options, previous_options=None):
        options['projects'] = self._query_projects(options)

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals):
        lines = []
        projects = options['projects']

        unique_projects = self.env['project.project'].search([])
        for project in unique_projects:
            lines.append((0, {
                'id': f'''~project.project~{project.id}''',
                'name': project.name,
                'search_key': project.name,
                'columns': self._get_columns(project.id, projects, options),
                'level': 1,
                'unfoldable': False,
                'unfolded': False,
            }))
        return lines
    
    def _query_projects(self, options):
        """
        Get sums for the initial balance.
        """
        project_data = []
        self.env['project.project'].search([])
        self._cr.execute(f"""
            SELECT
                project_project.id,
                project_project.company_id,
                project_project.analytic_account_id,
                sale_order_line.currency_id,
                sale_order.date_order                                                         AS date,
                project_project.name                                                          AS project,
                sale_order_line.qty_to_invoice                                                AS sale_order_qty,
                SUM(sale_order_line.price_unit)                                               AS sale_order_revenue
            FROM project_project
            INNER JOIN account_analytic_line
            ON project_project.id = account_analytic_line.project_id
            INNER JOIN sale_order_line
            ON account_analytic_line.so_line = sale_order_line.id
            INNER JOIN sale_order
            ON sale_order_line.order_id = sale_order.id
            INNER JOIN product_product
            ON product_product.id = sale_order_line.product_id
            INNER JOIN product_template
            ON product_template.id = product_product.product_tmpl_id
            WHERE sale_order_line.invoice_status = 'to invoice'
            GROUP BY project_project.id, sale_order_line.currency_id, sale_order.date_order, sale_order_qty
        """)
        project_data += self._cr.dictfetchall()
        self._cr.execute(f"""
            SELECT
                project_project.id,
                project_project.company_id,
                project_project.analytic_account_id,
                account_analytic_line.currency_id,
                account_analytic_line.date                                                    AS date,
                project_project.name                                                          AS project,
                SUM(account_analytic_line.amount)                                             AS timesheet_cost
            FROM project_project
            INNER JOIN account_analytic_line
            ON project_project.id = account_analytic_line.project_id
            GROUP BY project_project.id, account_analytic_line.currency_id, account_analytic_line.date
        """)
        project_data += self._cr.dictfetchall()
        self._cr.execute(f"""
            SELECT
                project_project.id,
                project_project.company_id,
                project_project.analytic_account_id,
                account_move_line.currency_id,
                account_move.date                                                             AS date,
                project_project.name                                                          AS project,
                account_move_line.quantity                                                    AS invoice_qty,
                SUM(account_move_line.price_unit)                                             AS invoice_revenue
            FROM project_project
            INNER JOIN (
                    SELECT 
                        jsonb_object_keys(analytic_distribution)                              AS analytic_account_id,
                        account_move_line.currency_id,
                        account_move_line.quantity,
                        account_move_line.price_unit,
                        account_move_line.move_id
                    FROM account_move_line
                    WHERE account_move_line.analytic_distribution IS NOT NULL
                ) account_move_line ON project_project.analytic_account_id::varchar(255) = account_move_line.analytic_account_id
            INNER JOIN account_move
                ON account_move.id = account_move_line.move_id
            WHERE account_move.state IN ('draft','to_approve','approved','posted')
            GROUP BY project_project.id, account_move_line.currency_id, account_move.date, invoice_qty
        """)
        project_data += self._cr.dictfetchall()
        self._cr.execute(f"""
            SELECT
                project_project.id,
                project_project.company_id,
                hr_expense.currency_id,
                hr_expense.date                                                               AS date,
                SUM(hr_expense.total_amount)                                                  AS expense_amount
            FROM project_project
            INNER JOIN (
                    SELECT 
                        jsonb_object_keys(analytic_distribution)                              AS analytic_account_id,
                        hr_expense.currency_id,
                        hr_expense.date,
                        hr_expense.total_amount
                    FROM hr_expense
                    WHERE hr_expense.analytic_distribution IS NOT NULL
                        AND hr_expense.state IN ('approved','done')
                ) hr_expense ON project_project.analytic_account_id::varchar(255) = hr_expense.analytic_account_id
            GROUP BY project_project.id, project_project.company_id, hr_expense.date, hr_expense.currency_id
        """)
        project_data += self._cr.dictfetchall()
        projects = self.filter_projects_by_column(project_data, options)
        return projects
    
    def filter_projects_by_column(self, project_data, options):
        projects = {}
        columns = options['columns']
        date_ranges = []
        for column in columns:
            filters = re.findall("'([^']*)'", column['column_group_key'])
            date_range = (datetime.strptime(filters[3], '%Y-%m-%d'), datetime.strptime(filters[5], '%Y-%m-%d'))
            column['date_from'] = date_range[0]
            column['date_to'] = date_range[1]
            date_ranges.append(date_range)
        for date_range in date_ranges:
            for project in project_data:
                if isinstance(project['date'], datetime):
                    project['date'] = project['date'].date()
                if date_range[0].date() <= project['date'] <= date_range[1].date():
                    usd_currency = self.env['res.currency'].search([('name', '=', 'USD')])
                    from_currency = self.env['res.currency'].browse([project['currency_id']])
                    currency_conversion_rate = self.env['res.currency']._get_conversion_rate(from_currency,usd_currency,self.env['res.company'].browse([project['company_id']]),project['date'].strftime("%m/%d/%y"))
                    id_date = '{}|{}'.format(project['id'],date_range[1].strftime('%Y-%m-%d'))
                    if id_date not in projects.keys():
                        projects[id_date] = {
                            'revenue': 0,
                            'cost': 0
                        }
                    projects[id_date]['revenue'] += project.get('sale_order_qty', 0) * project.get('sale_order_revenue', 0) * currency_conversion_rate
                    projects[id_date]['revenue'] += project.get('invoice_qty', 0) * project.get('invoice_revenue', 0) * currency_conversion_rate
                    projects[id_date]['cost'] += project.get('timesheet_cost', 0) * currency_conversion_rate
                    projects[id_date]['cost'] -= project.get('expense_amount', 0) * currency_conversion_rate
                    project.update({
                        'sale_order_revenue': 0,
                        'timesheet_cost': 0,
                        'expense_amount': 0,
                        'invoice_revenue': 0
                    })
        return projects

    def _get_columns(self, id, projects, options):
        columns_values = []
        columns = options['columns']
        for column in columns:
            id_date = '{}|{}'.format(id,column['date_to'].strftime('%Y-%m-%d'))
            if projects.get(id_date, False):
                project = projects[id_date]
                formatted_value = value = 0
                cost = project['cost']
                revenue = project['revenue']
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
            else:
                if column['name'] == 'Margin %':
                    formatted_value = '0.00\xa0%'
                else:
                    formatted_value = '$\xa00.00'
                columns_values.append({
                    'name': formatted_value,
                    'no_format': 0,
                    'class': 'number',
                })
        return columns_values
    