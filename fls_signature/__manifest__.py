# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'FLS: Smart Employee Contract Signature',
    'version': '1.1',
    'category': 'Customization',
    'description': """
        Task ID: 3724021
        Quadgram: dipa

        [REF:322] Implement Employee Contract Signature in Odoo
    """,
    'author': 'Odoo Inc',
    'website': 'http://www.odoo.com',
    'license': 'OPL-1',
    'depends': ['sign', 'hr'],
    'data': [
        'views/sign_item_type_views.xml',
    ],
    'installable': True,
}
