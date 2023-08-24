{
    'name': "Employees are set as Vendors",
    'summary': 'Able to set partners as vendors',
    'sequence': 100,
    'license': 'OPL-1',
    'website': 'https://www.odoo.com',
    'version': '16.0',
    'author': 'Odoo Inc',
    'description': """
Task ID: 3434925
The client needs a quick way to visualize its vendors when creating an RFQ. They are looking forward to implementing a checkbox to easily toggle on or off if a contact is a vendor. 

During the Purchase workflow, when selecting a vendor, the client also wants to filter the contacts available to select from; only contacts marked as vendors in the previous checkbox will be visible to the user to select.
    """,
    'depends': ['contacts', 'purchase'],
    'data': [
        'data/actions.xml',
        'views/res_partner_views.xml',
        'views/purchase_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
