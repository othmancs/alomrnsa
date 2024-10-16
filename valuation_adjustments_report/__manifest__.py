{
    'name': 'Valuation Adjustments Report',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Report for Valuation Adjustments grouped by product',
    'description': """
    This module provides a detailed report for Valuation Adjustments grouped by product.
    """,
    'author': 'Othman Almashaqba',
    'depends': ['stock', 'account'],
    'data': [
        'views/report_template.xml',
        'views/report_action.xml',
    ],
    'installable': True,
    'application': False,
}
