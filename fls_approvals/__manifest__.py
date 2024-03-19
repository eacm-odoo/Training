{
    'name': "Rule Based Workflow for Specific Models",
    'summary': 'Able to set approvals for Bills,Invoices, SOs,POs',
    'sequence': 100,
    'license': 'OPL-1',
    'website': 'https://www.odoo.com',
    'version': '16.0',
    'author': 'Odoo Inc',
    'description': """
Task ID: 3434926
This feature that will allow the admin (specific users) to set up approval rule(s) for the workflows 
(specific to Sale Order, Purchase Order, Invoice, Bill, and Journal Entry) based on different conditions/ attributes explained later in this document.
    """,
    'depends': ['sale', 'purchase','account','base'],
    'data': [
        'data/ir_sequence.xml',
        'security/approvals_security.xml',
        'security/groups.xml',
        'data/mail_template_approval.xml',
        'views/sale_orderview_inherit.xml',
        'views/approval_rules_form_view.xml',
        'views/purchase_order_form_view.xml',
        'views/account_move_form_view.xml',
        'security/ir.model.access.csv',
        'views/rejection_message_wizard_view.xml'
        
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
