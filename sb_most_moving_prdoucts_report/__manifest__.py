# -*- coding: utf-8 -*-
{
    'name': "SB Most Moving Prdoucts Report",
    'version': '0.1',
    'depends': ['base', 'sale', 'multi_branch_base', 'account', 'sb_seller_field', 'report_xlsx',
                'sb_sale_edit_and_reports'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/most_moving_product.xml',
        'reports/most_moving_product_report.xml'
    ],
}
