# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Branch Base',
    'version': '16.0.0.1',
    'category': 'Sales',
    'summary': 'Multiple Branch Base Multi Branch base Multiple Unit multiple Operating unit sales branch Multi Branches multi company multi branch multi company multiple unit operation multi unit multiple operation multi operation invoice multi branch unit base odoo',
    "description": """
       
       Base Multi Branch in Odoo,
       Base Branch in odoo,
       manage branch master in odoo,
       Set Branch on Contacts in odoo,
       Multi Branch Concept in odoo,
       multiple Branch for customer in odoo,
       multiple Branch for user in odoo,
       multiple Branch for contact in odoo,
    
    """,
    'author': 'BrowseInfo',
    "price": 10,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'depends': ['base', 'web'],
    'data': [
        'security/branch_security.xml',
        'security/multi_branch.xml',
        'security/ir.model.access.csv',
        'views/res_branch_view.xml',
        'views/inherited_res_users.xml',
        'views/inherited_partner.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'bi_branch_base/static/src/xml/branch.xml',
            'bi_branch_base/static/src/js/branch_service.js',
            'bi_branch_base/static/src/js/session.js',
        ]
    },
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/T6MMTsIQjto',
    "images": ['static/description/Banner.gif'],
    'post_init_hook': 'post_init_hook',
}

