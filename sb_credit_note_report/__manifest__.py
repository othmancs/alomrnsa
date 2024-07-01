# -*- coding: utf-8 -*-
{
    'name': "SB Credit Note Report",
    'version': '0.1',
    'depends': ['base', 'sale', 'multi_branch_base', 'account', 'sb_seller_field', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'wizard/credit_note.xml',
        'reports/credit_note_report.xml',
    ],
}
