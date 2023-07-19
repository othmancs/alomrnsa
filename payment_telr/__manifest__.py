# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': "Telr Payment Provider",
    'version': '16.0.1.1',
    'category': 'Accounting/Payment Providers',
    'summary': 'Telr Payment Gateway - One of the widely used payment gateway used in the UAE integrated with odoo ecommerce | Telr Payment Gateway | Telr Payement Acquirer | Telr Payement Provider | AED Online Payment | AED Debit Card Payment | AED E-commerce payment | AED Online sale payment | AED Online card payment',
    'description': """
Telr Payment Gateway
================================
One of the widely used payment gateway used in the UAE integrated with odoo ecommerce'
    """,
    'license': 'OPL-1',
    'author': "Kanak Infosystems LLP.",
    'website': "https://www.kanakinfosystems.com",
    'images': ['static/description/banner.jpg'],
    'depends': ['payment'],
    'data': [
        'views/payment_telr_templates.xml',
        'views/payment_provider_views.xml',
        'data/telr_payment_data.xml',
    ],
    'installable': True,
    'price': 69,
    'currency': 'EUR',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
