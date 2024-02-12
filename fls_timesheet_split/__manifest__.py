# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'FLS: Split Timesheet Lines',
    'version': '1.0',
    'category': 'Customization',
    'description': """
        Task ID: 3724014
        Quadgram: dipa
    """,
    'author': 'Odoo Inc',
    'website': 'http://www.odoo.com',
    'license': 'OPL-1',
    'depends': ['timesheet_grid', 'sale_management', 'fls_planning_timesheet_generation'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_analytic_line_split.xml'
    ],
    'installable': True,
}
