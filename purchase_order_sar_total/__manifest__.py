{
    'name': 'Purchase Order SAR Total',
    'version': '1.0',
    'category': 'Purchases',
    'summary': 'Displays total in SAR alongside USD for purchase orders with USD vendors',
    'description': """
        This module adds a computed field to display the total amount in SAR 
        alongside the USD total in purchase orders when the vendor's currency is USD.
    """,
    'author': 'Essam Al Mahi',
    'depends': ['purchase'],
    'data': [
        'views/purchase_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
