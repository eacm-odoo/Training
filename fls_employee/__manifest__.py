{
    'name': 'FLS: Employee',
    'summary': '''Modifications involving the employees module''',
    'author': 'Odoo Inc',
    'developers': ['Lars Gartenberg (laga)', 'Zeno Nanon (zna)'],
    'task_ids': ['3434934','3434930'],
    'website': 'https://www.odoo.com/',
    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['hr', 'hr_contract', 'sale_project', 'sale_timesheet', 'account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'views/fls_geo_views.xml',
        'views/hr_employee_views.xml',
        'views/res_users_views.xml',
        'data/actions.xml',
        'data/employee_margin_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fls_employee/static/src/js/*.js',
        ],
    },
    'application': False,
    'auto_install': False,
    'installable': True,
}
