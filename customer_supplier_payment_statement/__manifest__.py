# -*- coding: utf-8 -*-
{
    'name': 'Customer / Vendor Statement',
    'version': '16.0',
    'summary': "Customer / Vendor  Statement Reports",
    'sequence': 16,
    'description': """
                    Odoo Account Reports
                    """,
    'category': 'purchase',
    'author': 'Biztech Computer',
    'maintainer': 'Biztech Computer',
    'website': 'https://biztechbh.biz',
    'depends': ['account', 'purchase', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'reports/report.xml',
        'views/res_partner_views.xml',
        'reports/report_template.xml',
        'wizard/customer_statement_wizard.xml',
        'reports/vendor_report_template.xml',
        'data/ir_cron_data.xml'
    ],
    'assets': {
        'web.assets_backend': [
            '/customer_vendor_statement/static/src/js/action_manager.js',
        ]
    },
    'demo': [],
    'license': 'AGPL-3',
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}