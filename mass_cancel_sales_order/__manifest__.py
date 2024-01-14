# -*- coding: utf-8 -*-
{
    'name': 'Mass Cancel Sales Order',
    'summary': "Mass Cancel Sales Order",
    'description': "Mass Cancel Sales Order",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    'support': 'ipredictitsolutions@gmail.com',

    'category': 'Sales',
    'version': '16.0.0.1.0',
    'depends': ['sale_management'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_order_cancel.xml',
    ],

    'license': "OPL-1",
    'auto_install': False,
    'installable': True,

    'images': ['static/description/banner.png'],
    'pre_init_hook': 'pre_init_check',
}
