# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Res Documents",
    'summary': "Res Documents",
    'description': """
        Allow specific user to add documents and generate expiry documents notification
        """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr'],
    'data': [
        'data/document_type_data.xml',
        'data/res_documents_cron.xml',
        'data/email_template.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_documents_view.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
