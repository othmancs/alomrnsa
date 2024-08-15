# -*- coding: utf-8 -*-
{
    'name': "SB Sales Per Day Report",
    'version': '0.1',
    'depends': ['base', 'sale', 'multi_branch_base', 'account', 'sb_seller_field', 'report_xlsx', 'sb_sale_edit_and_reports'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sales_per_day.xml',
        'reports/sales_per_day_report.xml',
    ],
}
