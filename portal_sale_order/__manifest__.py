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

            'portal_sale_order/static/lib/select4/css/select4.min.css',
            'portal_sale_order/static/src/css/select4-bootstrap.min.css',
            'portal_sale_order/static/lib/select4/js/select4.min.js',
        ],
        'web.assets_frontend': [
            'portal_sale_order/static/src/js/portal_form.js',
            'portal_sale_order/static/src/js/portal_sale_order.js',
            'portal_sale_order/static/lib/select4/css/select4.min.css',
            'portal_sale_order/static/src/css/select4-bootstrap.min.css',
            'portal_sale_order/static/lib/select4/js/select4.min.js',
        ],

    },
}
