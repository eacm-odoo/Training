{
    'name': 'FLS Attachment Limit',
    'summary': '''''',
    'description': '''''',
    'author': 'Odoo Inc',
    'developers': ['Lars Gartenberg (laga)'],
    'task_ids': ['',],
    'website': 'https://www.odoo.com/',
    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OPL-1',
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'depends': [
        'base',
        'base_setup',
        'web',
    ],
    'assets': {
        'web.assets_frontend': [
            'fls_attachment/static/src/js/limit_upload_size.js',
        ],
        # 'mail.assets_messaging': [
        #     #('include', 'mail.assets_core_messaging'),
        #     'fls_attachment/static/src/js/limit_upload_size.js',
        # ],
    },
    'application': False,
    'auto_install': False,
    'installable': True,
}
