# -*- coding: utf-8 -*-
{
    'name': "SB Sale Order Report",
    'version': '0.1',
    'depends': ['base', 'sale', 'multi_branch_base', 'account', 'sb_seller_field', 'report_xlsx', 'sb_sale_edit_and_reports'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_order.xml',
        'reports/sale_order_report.xml',
    ],
}
