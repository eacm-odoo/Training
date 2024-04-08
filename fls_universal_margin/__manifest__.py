# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'FLS: Universal Margin Report',
    'version': '1.0',
    'category': 'Customization',
    'description': """
        Task ID: 3750293
        Quadgram: dipa
    """,
    'author': 'Odoo Inc',
    'website': 'http://www.odoo.com',
    'license': 'OPL-1',
    'depends': ['fls_employee', 'fls_approvals'],
    'data': [
        'security/ir.model.access.csv',
        'views/marginality_data_views.xml',
        'views/analytic_account_history_views.xml',
        'wizard/marginality_data_initializer_wizard_views.xml',
    ],
    'installable': True,
}
