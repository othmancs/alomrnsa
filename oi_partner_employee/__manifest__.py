# -*- coding: utf-8 -*-
{
'name': 'Contacts Employee Filter',
'summary': 'Contacts Employee Filter, Employee, Contacts, HR, Human Resources, Filter, '
           'Filtering, Search, Openinside, Odoo',
'version': '16.0.1.1.2',
'category': 'Human Resources',
'website': 'https://www.open-inside.com',
'description': '''
'''
               '''		* Add employee filter to contacts.
'''
               '''		* Employee User/Home Address match check.
'''
               '''		* User link to only one employee check.
'''
               '''		* Contact link to only one employee check.
'''
               '''		* Unset default customer for an employee.
'''
               '    ',
'images': ['static/description/cover.png'],
'author': 'Openinside',
'license': 'OPL-1',
'price': 0.0,
'currency': 'USD',
'installable': True,
'depends': ['hr', 'account'],
'data': ['view/res_partner.xml', 'view/hr_employee.xml', 'view/action.xml'],
'post_init_hook': 'post_init_hook',
'odoo-apps': True,
'application': False
}