# -*- coding: utf-8 -*-
{
    'name': "Mass Cancel Confirm Journal",
    'summary': """ This module allows to Cancel or Confirm mass/bulk/multiple Journal Entries
            from the tree view.""",
    'author': "Laxicon Solution",
    'website': "www.laxicon.in",
    'sequence': 101,
    'support': 'info@laxicon.in',
    'category': 'Accounting',
    'version': '16.0.1.0.0',
    'license': "LGPL-3",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/journal_entries_cancel_wizard.xml',
        'wizard/journal_entries_confirm_wizard.xml',
        'views/cancel_journal_entries_view.xml',
    ],
    'images':  ["static/description/banner.png"],
    'installable': True,
    'auto_install': False,
}
