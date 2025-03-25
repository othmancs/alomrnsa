{
    'name': 'Non Counted Products in Inventory',
    'version': '16.0.1.0.0',
    'summary': 'Show non-counted products in inventory adjustments',
    'description': """
        This module adds a feature to display products that were not counted 
        during inventory adjustments.
    """,
    'author': 'OthmanCs',
    'website': 'https://www.yourwebsite.com',
    'category': 'Inventory/Inventory',
    'depends': ['stock'],
    'data': [
        'views/inventory_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}