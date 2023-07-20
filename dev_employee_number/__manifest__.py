# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Employee Number',
    'version': '1.0',
    'sequence': 1,
    'category': 'Generic Modules/Human Resources',
    'description':
        """
This Module add below functionality into odoo

        1.This module helps you to display unique Employee Number on Employee screen

    """,
    'summary': 'Odoo app will add Employee Number on Employee screen',
    'author': 'Devintelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',
    'depends': ['hr'],
    'data': [
        'views/employee_sequence.xml',
        'views/employee_view.xml'
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    #author and support Details ==========#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'pre_init_hook' :'pre_init_check',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
