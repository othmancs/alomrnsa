# -*- coding: utf-8 -*-
{
    'name': "SB Profit and Loss By Category Report",
    'version': '0.1',
    'depends': ['base', 'sale', 'multi_branch_base', 'account', 'sb_seller_field', 'report_xlsx', 'sb_sale_edit_and_reports'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/profit_loss_by_category.xml',
        'reports/profit_loss_by_category.xml',
    ],
}
