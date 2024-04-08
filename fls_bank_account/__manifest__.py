{
    'name': 'FLS - Bank Account',
    'summary': '''Fill in bank account information for customer invoices and vendor bills where needed.''',
    'description': """
        On customer invoices and vendor bills, there are two similar fields for bank accounts. 
        Regardless of the purpose, it may cause confusion and make room for functional errors.
        Task ID: 3819713
        Quadgram: cmgv
    """,
    'category': 'Customization',
    'version': '1.0.0',
    'author': 'Odoo Development Services',
    'maintainer': 'Odoo Development Services',
    'website': 'http://www.odoo.com',
    'license': 'OPL-1',
    'depends':['base', 'base_setup', 'account_accountant', 'fls_reports'],
    'data': [
        'views/account_move_form_view.xml',
        'report/invoice_report.xml'
    ],
}
