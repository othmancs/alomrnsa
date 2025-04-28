{
    'name': 'Duplicate Internal Reference Filter',
    'version': '16.0.1.0.0',
    'summary': 'Filter products with duplicate internal references',
    'description': """
        Adds a filter to show products with duplicate internal references.
    """,
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'license': 'AGPL-3',
    'depends': ['product'],
    'data': [
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
}