{
    'name': 'Tax Amount on Sale Order',
    'version': '16.0.0.0',
    'author': 'INKERP',
    'summary': 'Tax Amount in Sale Order.',
    'description': """This module helps to show Tax Amount in Sale Order.""",
    'category': 'Sale',
    'website': 'https://www.INKERP.com/',
    'depends': ['sale'],

    'data': [
        'views/sale_order_view.xml',
        'report/sale_report_templates.xml',
    ],

    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
