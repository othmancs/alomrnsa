# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'CRM Kanban View',
    'version': '16.0.1.0.0',
    'sequence': 1,
    'summary': """
        New Design Kanban View, New Style Kanban View, Web Responsive Kanban View, Advanced Kanban View, 
        Design Card View, Style Card, Responsive Card, Advanced Card, 
        Responsive CRM Kanban View, CRM KanbanView, Responsive CRM Card View, Advanced CRM CardView, 
        Responsive Customer Kanban View, Customer KanbanView, Responsive Customer Card View, Advanced Customer CardView, 
        Responsive Contact Kanban View, Advanced Contact KanbanView, Responsive Contact Card View, Advanced Contact CardView, 
        Responsive Partner Kanban View, Advanced Partner KanbanView, Responsive Partner Card View, Advanced Partner CardView
    """,
    'description': "The new style of kanban view offers an amazing view of partner details.",
    'author': 'NEWAY Solutions',
    'maintainer': 'NEWAY Solutions',
    'price': '0',
    'currency': 'USD',
    'website': 'https://neway-solutions.com',
    'license': 'LGPL-3',
    'images': [
        'static/description/screenshot.gif'
    ],
    'depends': [
        'base',
    ],
    'data': [
        'views/card.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'kanban_crm/static/src/scss/card.scss',
        ],
    },
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [

    ],
}
