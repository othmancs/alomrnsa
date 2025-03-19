# -*- coding: utf-8 -*-
{
    'name': 'Account Reports',
    'version': '15.0',
    'summary': "Account Reports",
    'sequence': 15,
    'description': """
                    Odoo Account Reports
                    """,
    'category': 'Accounting',
    'author': 'Knowledge Bonds',
    'maintainer': 'Knowledge Bonds',
    'website': '',
    'depends': ['account', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_report_view.xml',
        'reports/report.xml',
        'reports/account_report_template.xml',

             ],
    'demo': [],
    'license': 'AGPL-3',
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
