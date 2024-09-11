# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "HR Fiscal Year",
    'summary': """ HR Fiscal Year """,
    'description': """ Calendar Year For Public Holiday Duration and Year period""",
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'Human Resource/Employee',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/fiscal_year_data.xml',
        'views/hr_fiscal_year_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
