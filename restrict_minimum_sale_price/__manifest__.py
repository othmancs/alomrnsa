{
    'name': 'Restrict Minimum Sale Price',
    'version': '16.0.1.0.0',
    'category': 'Sales',
    'summary': 'Restrict sale price to be no less than the selected pricelist amount.',
    'description': """
        This module ensures that the sale price on sale order lines cannot be lower
        than the corresponding price in the selected pricelist. Users can only set
        a price equal to or higher than the pricelist price.
    """,
    'author': 'Othmancs',
    'depends': ['sale'],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
