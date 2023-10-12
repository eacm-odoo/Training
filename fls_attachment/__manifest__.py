{
    'name': 'FLS Attachment Limit',
    'summary': '''Restricts the file attachment upload size to the specified attachment limit config parameter.''',
    'author': 'Odoo Inc',
    'developers': ['Lars Gartenberg (laga)'],
    'task_ids': ['3434931',],
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
        'mail',
    ],
    'assets': {
        'web.assets_backend': [
            'fls_attachment/static/src/js/limit_upload_size.js',
            'fls_attachment/static/src/scss/attachment_limit.scss',
        ],
    },
    'application': False,
    'auto_install': False,
    'installable': True,
}
