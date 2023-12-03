# -*- coding: utf-8 -*-


{
    'name': 'Accounting Print Journal Entries Report in Odoo',
    'version': '17.0.0.0',
    'category': 'Account',
    'license': 'OPL-1',
    'summary': 'Allow to print pdf report of Journal Entries in Accounting.',
    'description': """
    Allow to print pdf report of Journal Entries.
    print journal entry accounting
    print journal entry reports
    account journal entry reports
    accounting entry reports
""",
    'author': 'Musa Abdullah',
    'depends': ['base','account'],
    'data': [
            'report/accounting_print_report_journal_entries_view.xml',
            'report/accounting_print_report_report_journal_entries.xml',
    ],
    'installable': True,
    'auto_install': False,
    "images":["static/description/Banner.gif"],
}

