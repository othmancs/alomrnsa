# -*- coding: utf-8 -*-

{
    "name": "sb_quantities_sold_report",
    "version": "1.0.0.16",
    "depends": [
        'base', 'sale', 'multi_branch_base', 'account', 'sb_seller_field', 'report_xlsx'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/quantities_sold_wizard.xml',
        'reports/quantities_sold_report.xml',



    ],
    "installable": True,
    "auto_install": False,
}
