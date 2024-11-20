{
    'name': 'Cycle Counting Missing Items Report',
    'version': '1.0',
    'summary': 'Generate report for missing items in Interim Cycle Counting',
    'description': 'A module to generate a report of items not counted during Interim Cycle Counting in Odoo 16.',
    'author': 'Othmancs92',
    'depends': ['stock'],  # الوحدة تعتمد على المخزون
    'data': [
        'views/inventory_report_action.xml',
        'reports/inventory_report_template.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}