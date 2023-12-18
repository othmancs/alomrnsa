{
    'name': 'Product Certificates',
    'summary': 'Manage product certificates with ease, featuring tracking, and customizable features.',
    'description': '''
        This module empowers users to efficiently create and organize product certificates. 
        Track statuses, utilize visual classifications, assign priorities, 
        and benefit from customizable stages and tags for a tailored certificate management experience.
    ''',
    'version': '17.0.1.0',
    'category': 'Inventory',
    'license': 'LGPL-3',
    'images': ['static/description/eqp_product_certificates.gif'],
    'author': 'EQP Solutions',
    'website': 'https://www.eqpsolutions.com/',
    'contributors': [
        'Esteban Quevedo <esteban.quevedo@eqpsolutions.com>',
    ],
    'depends': ['stock'],
    'data': [
        'security/product_certificate_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/product_certificate_views.xml',
        'views/product_certificate_stage_views.xml',
        'views/product_certificate_tag_views.xml',
        'views/product_views.xml',
        'report/product_certificate_templates.xml',
        'report/product_certificate_reports.xml',
        'report/product_certificate_report_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'eqp_product_certificate/static/src/**/*',
        ],
    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
