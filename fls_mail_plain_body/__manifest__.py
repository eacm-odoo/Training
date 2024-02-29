# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'FLS - Plain Text Email Template',
    'version': '1.0',
    'category': 'Customization',
    'description': """
        Task ID:  3724018
        Quadgram: dipa
    """,
    'author': 'Odoo Inc',
    'website': 'http://www.odoo.com',
    'license': 'OPL-1',
    'depends': ['mail'],
    'data': [ 
        'views/mail_template_views.xml',
        'data/mail_template_data.xml',
    ],
    'installable': True,
}
