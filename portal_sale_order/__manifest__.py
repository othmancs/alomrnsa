# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Portal',
    'description': "",
    'depends': ['portal', 'sale', 'multi_branch_base', 'web_editor'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/portal_templates.xml',
        # 'views/hr_employee.xml',
        # 'views/approval_category.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_common': [
            ('replace', 'web/static/lib/select2/select2.css',
             'portal_sale_order/static/lib/select2/css/select2.min.css'),
            ('replace', 'web/static/lib/select2-bootstrap-css/select2-bootstrap.css',
             'portal_sale_order/static/src/css/select2-bootstrap.min.css'),
            ('replace', 'web/static/lib/select2/select2.js',
             'portal_sale_order/static/lib/select2/js/select2.min.js'),
            'portal_sale_order/static/src/js/common/**/*',

        ],
        'web.assets_frontend': [
            'portal_sale_order/static/src/js/portal_form.js',
            'portal_sale_order/static/src/js/portal_sale_order.js',
            ('replace', 'web/static/lib/select2/select2.css',
             'portal_sale_order/static/lib/select2/css/select2.min.css'),
            ('replace', 'web/static/lib/select2-bootstrap-css/select2-bootstrap.css',
             'portal_sale_order/static/src/css/select2-bootstrap.min.css'),
            ('replace', 'web/static/lib/select2/select2.js',
             'portal_sale_order/static/lib/select2/js/select2.min.js'),
            'portal_sale_order/static/src/js/common/**/*',

        ],

    },
}
