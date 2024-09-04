# -*- coding: utf-8 -*-

{
    "name": "sb_profitable_clients_report",
    "version": "1.0.0.16",
    "depends": [
        'base', 'sale', 'multi_branch_base', 'account', 'sb_seller_field', 'report_xlsx'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/profitable_clients_wizard.xml',
        'reports/profitable_clients_report.xml',



    ],
    "installable": True,
    "auto_install": False,
}
