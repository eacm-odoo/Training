{
    'name': "First Line Software - Timesheet Generation",
    'summary': """Generate timesheets from the Planning app""",
    'description': """
Select slot from the planning app to generate timesheets automatically based on employees' calendars.
        """,
    'author': "Odoo Inc",
    'developers': ["John Truong (jot)"],
    'task_ids': [2962300],
    'website': "https://www.odoo.com/",
    'category': "Custom Development",
    'version': "1.0",
    'license': "OPL-1",
    'depends': ['planning', 'hr_timesheet','project_forecast','project_timesheet_forecast'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/generate_timesheets_views.xml',
        'views/planning_slot_views.xml',
    ],
    'application': False,
    'auto_install': False,
    'installable': True
}
