{
    'name': "Custom Group for Chatter to be Editable & disable/Revoke access for all the clickable fields on Employee Form",
    'summary': 'New group for permanent chatter access',
    'sequence': 100,
    'license': 'OPL-1',
    'website': 'https://www.odoo.com',
    'version': '16.0',
    'author': 'Odoo Inc',
    'description': """
Task ID: 3187765
Users of the new user group should also have access to chatter to be able to send message, log note, schedule activities , add/ remove followers, add upload attachment.
    """,
    'depends': ['mail', 'hr'],
    'data': [
        'security/groups.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
