{
    'name': 'Product Shipment Cost Report',
    'version': '1.0',
    'author': 'Your Name',
    'category': 'Warehouse',
    'summary': 'Print product cost report for shipments in Landed Costs',
    'description': 'This module calculates and prints the total product cost for shipments within the Landed Costs module.',
    'depends': ['stock', 'account'],  # الموديولات التي يعتمد عليها الموديول
    'data': [
        'views/shipment_cost_report_template.xml',
        'reports/shipment_cost_report.xml',
    ],
    'installable': True,
    'application': False,
}