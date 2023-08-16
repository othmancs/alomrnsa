# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Type Menu',
    'version': '14.0.1.0',
    'category': 'accounting',
    'summary': 'Account Type is a parent account being used in Odoo Chart of Account to defined child accounts',    # Author
    'author': 'Mediod Consulting Pvt. Ltd.',
    'website': 'http://www.mediodconsulting.com/',
    'maintainer': 'Mediod Consulting Pvt. Ltd.',
    'description': """This module will add menu under account configuration menu to add a new menu for account.account.type

Account Type is a parent account being used in Chart of Account to defined child accounts.

menu to add or replace or update account type in chart of account.
Odoo Odoo Accounts""",
    'sequence': -100,
    'depends': ['account'],
    'data': [
        'views/account_type_menu.xml'
    ],
    'demo': [
    ],
    "images": ['static/description/Banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}