# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
{
    "name": "BSTT Account Invoice",
    "summary": "Extends the Account Invoice "
               "amount",
    "version": "14.0.1.0.0",
    "category": "Invoicing",
    "website": "https://bstt.com.sa/",
    "author": "BSTT",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ['base', 'web', 'l10n_gcc_invoice', 'l10n_sa', 'l10n_sa_invoice'],
    "data": [
        'security/account_security.xml',
        # 'views/assets.xml',
        'views/company.xml',
        'views/account_move.xml',
        'reports/invoice_report.xml',
        'reports/base_document_layout.xml',
    ],
    'qweb': [

    ],
}
