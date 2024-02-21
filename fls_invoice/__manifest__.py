{
    'name': "First Line Software - Invoice Views",
    'summary': """Refactor Invoice views""",
    'description':  """
                    [REF:313] Invoice Views Improvement        
                    """,
    'author': "Odoo Inc",
    'developers': ["Kusal Nagabhairava (kusn)"],
    'task_ids': [3724019],
    'website': "https://www.odoo.com/",
    'category': "Custom Development",
    'version': "1.0",
    'license': "OPL-1",
    'depends': ['sale','account'],
    'data': [
        'views/view_account_invoice_filter.xml',
        'views/view_account_invoice_form_view.xml'
    ],
}
