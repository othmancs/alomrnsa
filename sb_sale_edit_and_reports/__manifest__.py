# -*- coding: utf-8 -*-

{
    "name": "sb_sale_edit_and_reports",
    "version": "1.0.0.16",
    "depends": [
        'base', 'sale', 'multi_branch_base', 'account', 'sb_seller_field', 'report_xlsx', 'contacts'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/views.xml',
        'views/branch_sales_comparison_wizard.xml',
        'reports/branch_sales_comparison_report.xml',
        'reports/sales_report.xml'


    ],
    "installable": True,
    "auto_install": False,
}
