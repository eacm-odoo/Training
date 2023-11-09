{
    'name': "Customization of invoice and bill templates",
    'summary': 'Customization of invoice and bill templates',
    'sequence': 100,
    'license': 'OPL-1',
    'website': 'https://www.odoo.com',
    'version': '16.0',
    'author': 'Odoo Inc',
    'description': """
Task ID: 3434932
This feature that will generate customized bills and invoices 
    """,
    'depends': ['sale', 'purchase','account'],
    'data': [
        "views/account_move_form_view.xml",
        "views/sale_order_view_form.xml",
        "views/res_partner_bank_form_view.xml",
        "report/invoice_report.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
