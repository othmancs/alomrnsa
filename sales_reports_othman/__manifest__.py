{
    'name': 'تقارير المبيعات',
    'version': '16.0.1.0.0',
    'summary': 'تقارير المبيعات اليومية',
    'description': "تقارير المبيعات اليومية مع ويزرد لتحديد التاريخ والفرع",
    'author': 'Othmancs',
    'website': 'http://www.yourcompany.com',
    'category': 'Sales',
    'depends': ['sale', 'account', 'multi_branch_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'reports/report_template.xml',
        'reports/reports.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
