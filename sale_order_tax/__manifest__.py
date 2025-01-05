{
    'name': 'Sale Order Tax Automation',
    'version': '16.0.1.0.0',
    'summary': 'Automatically set taxes in Sale Order Line based on customer settings.',
    'author': 'Essam Al Mahi',
    'depends': ['sale', 'account'],
    'data': ['views/sale_order_tax_view.xml', 'views/res_partner_tax_view.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
