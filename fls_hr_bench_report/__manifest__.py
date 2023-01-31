{
    'name': "First Line Software - Bench Report",
    'summary': """Track employee work times""",
    'description': """
Generate a bench report listing employees' planned, timesheeted, and wasted hours.
        """,
    'author': "Odoo Inc",
    'developers': ["John Truong (jot)"],
    'task_ids': [2962300],
    'website': "https://www.odoo.com/",
    'category': "Custom Development",
    'version': "1.0",
    'license': "OPL-1",
    'depends': ['planning', 'hr_timesheet','project_forecast','project_timesheet_forecast','project_timesheet_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/bench_report_date_views.xml',
        'reports/hr_bench_report_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fls_hr_bench_report/static/src/bench_report_list/bench_report.xml',
            'fls_hr_bench_report/static/src/bench_report_list/bench_report_list_controller.js',
            'fls_hr_bench_report/static/src/bench_report_list/bench_report_list_view.js',
        ]
    },
    'application': False,
    'auto_install': False,
    'installable': True
}
