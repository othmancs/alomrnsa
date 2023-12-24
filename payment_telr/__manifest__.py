{
    'name': "Telr Payment Gateway",
    'version': '16.0.1.1',
    'category': 'Accounting/Payment Providers',
    'summary': 'Telr Payment Gateway is a distinguished global payment gateway that provides businesses with a secure and hassle-free platform to accept online payments from their customers',
    'description': """
                    Telr Payment Gateway
                    ================================
                     Telr is an award-winning payment gateway provider, founded in 2014, and with offices in Singapore, the UAE, India, and Saudi Arabia'
                        """,
    'author': "Telr",
    'website': "https://telr.com/",
    'images': ['static/description/icon.png'],
    'depends': ['payment'],
    'data': [
        'views/payment_telr_templates.xml',
        'views/payment_provider_views.xml',
        'data/telr_payment_data.xml',
    ],
    
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_frontend': [
            'payment_telr/static/src/js/**/*',
        ],
    },
}