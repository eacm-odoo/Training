{
    'name': "First Line Software: Two Layers of Timesheet Validation",
    'summary': 'Modified Timesheet Validation',
    'sequence': 100,
    'license': 'OPL-1',
    'website': 'https://www.odoo.com',
    'version': '16.0',
    'author': 'Odoo Inc',
    'description': """
Task ID: 3235472
Project managers are responsible for getting right hours spent by their team members on their projects but not for verification of employees leaves or time spent on other projects. Resource managers, to the contrary, are primarily responsible for verification of time spent by each employee across the board – on projects, leaves, bench (downtime) etc.
    """,
    'depends': ['timesheet_grid'],
    'data': [
        'data/actions.xml',
        'views/hr_employee_views.xml',
        'views/hr_timesheet_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
