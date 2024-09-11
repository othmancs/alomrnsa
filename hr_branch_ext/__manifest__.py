# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name' : "HR Branch Ext",
    'summary': "HR Branch Ext",
    'description': """ Multi branches connected with saudi hr branch""",
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': [
        'saudi_hr_branch',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/branch.xml',
    ],
    'installable': True,
    'auto_install': False,
}
