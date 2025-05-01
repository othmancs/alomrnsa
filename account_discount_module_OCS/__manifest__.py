{
    'name': 'الخصم المسموح به (لا يتجاوز 1 ريال)',
    'version': '1.0',
    'summary': 'يسمح بإضافة خصم لا يتجاوز 1 ريال للفواتير',
    'description': """
        هذا الموديول يسمح بإضافة خصم على الفواتير بحد أقصى 1 ريال للكسور العشرية.
    """,
    'author': 'OTHMANCS',
    'website': 'https://www.yourwebsite.com',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}