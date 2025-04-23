# __manifest__.py

{
    'name': 'Purchase Order Landed Costs',
    'version': '16.0.1.0.0',
    'summary': 'Link Landed Costs to Purchase Orders',
    'description': """
        This module adds a field to Purchase Orders that shows the total 
        amount of related Landed Costs based on vendor bills.
    """,
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'depends': ['purchase', 'stock_landed_costs'],
    'data': [
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}