{
    'name': 'Product Cost by Warehouse',
    'version': '1.0',
    'summary': 'Tracks product costs by warehouse',
    'description': """
        This module adds the functionality to track the cost of products per warehouse.
        It introduces a new model to store product costs for each warehouse and integrates
        this functionality into product and warehouse forms.
    """,
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'category': 'Inventory',
    'depends': ['stock', 'product'],
    'data': [
        'views/product_product_view.xml',
        'views/stock_warehouse_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}