# -*- coding: utf-8 -*-
{
    'name': 'Dynamic Portal',
    'version': '1.0.0',
    'summary': """ Dynamic Portal """,
    'description': 'Dynamic Portal',
    'category': 'web',
    'author': 'Mahmoud Abd-Elaziz',
    'depends': ['portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/template.xml',
        'views/sharing_templates.xml',
        'views/portal.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'dynamic_portal/static/src/js/edit_one2many_lines.js',
            'dynamic_portal/static/src/js/onchange_buttons.js',
            'dynamic_portal/static/src/js/onchange_fields.js',
            'dynamic_portal/static/src/js/select2.js',
            'dynamic_portal/static/src/css/style.css',
        ],

    },
    'demo': [],
    'installable': True,
}
