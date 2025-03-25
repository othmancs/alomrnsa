{
    'name': 'Show Non-Counted Products',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Shows products not included in Inventory Adjustments',
    'description': 'Module to display products that were not included in any inventory adjustments.',
    'author': 'Othmancs',
    'website': 'http://yourwebsite.com',
    'depends': ['stock'],
    'data': [
        'views/inventory_adjustment_view.xml',
    ],
    'installable': True,
    'application': True,
}
