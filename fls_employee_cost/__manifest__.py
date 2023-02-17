{
    'name': "Employee Cost Calculation, Profitability (margin) Calculation & Report in USD",
    'summary': 'Modifications to hr, project and timesheet to view profitability more clearly',
    'sequence': 100,
    'license': 'OPL-1',
    'website': 'https://www.odoo.com',
    'version': '16.0',
    'author': 'Odoo Inc',
    'description': """
Task ID: 3132682
1) Calculate Employee cost
1.1) Add a new field ‘Salary Burden Rate’ under contract (hr.contract) which is going to be float and required field with 1.00 as the default value.
1.2) Add a new field ‘Full Cost in USD’ under the ootb ‘Cost’ field in the employee form.
2) Gross Margin and Profitability fields (Budget, Revenue, Cost & Margin) should be displayed in USD 
with the USD sign irrespective of the invoice/project currency and the company currency considering the 
updated exchange rate (whether it’s set manually/is linked to a bank or an exchange rate service). 
i.e. there is a project created under the Netherlands company with the currency as EUR however if user 
views it either while having the Netherlands company selected under the company options or any other 
company that has another currency, the Gross Margin and Profitability fields (Budget, Revenue, Cost & Margin) 
should be displayed in USD with USD sign.
3) Add a pivot view in the project.project model to enable user filter & group by one/ multiple projects 
(it should be included within the list view as well), at a minimum there needs to be the following fields/filters, 
the ootb download to excel feature needs to be there
4) Change the way Billable Time is being calculated; while calculating the % of Billable Time, exclude the adjusted hours.
For example, employee logs 8 hours of timesheet with Adjusted=False, his manager logs ‘-2’ hours with Adjusted=True, 
for the accounting part of the system it’s 8-2 hours which is 6, so invoices will be created only for 6 hours.
    """,
    'depends': ['hr', 'hr_contract', 'hr_payroll', 'project', 'sale_project', 'timesheet_grid'],
    'data': [
        'data/actions.xml',
        'views/hr_contract_views.xml',
        'views/hr_views.xml',
        'views/project_views.xml',
        'views/res_company_views.xml',
        'views/resource_calendar_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fls_employee_cost/static/src/components/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
