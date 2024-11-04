{
    'name': 'Remove Internal Reference(SKU) From Product Name',
    'version': '16.0.1.0.0',
    'category': 'Sales',
    'summery': ' Remove Internal Reference(SKU) or default code from Product Name',
    'author': 'INKERP',
    'website': "https://www.INKERP.com",
    'depends': ['product'],
    'data': [
        'views/product_template_view.xml',
        'views/product_product_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
    'currency': 'EUR',
}
