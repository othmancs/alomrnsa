{
    'name': 'Customer Fields in Sale Order and Invoice',
    'version': '16.0.1.0.0',
    'category': 'Sales',
    'summary': 'Add customer name and phone in sale order and invoice',
    'description': """
        This module allows you to add customer name and phone fields in the sale order form,
        and transfer them to the invoice form. The fields are editable in sale order and read-only in invoices.
    """,
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
}
