{
    'name': "FLS: Purchase",
    'summary': 'All modifications related to purchase module',
    'sequence': 100,
    'license': 'OPL-1',
    'website': 'https://www.odoo.com',
    'version': '16.0',
    'author': 'Odoo Inc',
    'description': """
Task ID: 3176750
-Added domain to contact
    """,
    'depends': ['purchase', 'account'],
    'data': [
        'data/actions.xml',
        'data/mail_template_data.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
