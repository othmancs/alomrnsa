# -*- coding: utf-8 -*-
{
    'name': "SB Saller Activity Report",
    'version': '0.1',
    'depends': ['base', 'sale', 'multi_branch_base', 'account', 'sb_seller_field', 'report_xlsx', 'sb_sale_edit_and_reports'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/total_seller_activity.xml.xml',
        'reports/seller_activity_report.xml',
    ],
}
