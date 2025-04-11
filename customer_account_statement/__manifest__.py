
{
    "name": "Customer Account Statement",
    "version": "1.0",
    "category": "Accounting",
    "summary": "Generate customer account statement in PDF and Excel",
    "depends": ["base", "account", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/account_statement_wizard_view.xml",
        "report/account_statement_report.xml",
        "report/account_statement_template.xml"
    ],
    "assets": {},
    "installable": True,
    "application": False,
}
