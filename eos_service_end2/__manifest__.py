{
    'name': 'EOS Service End Calculation',
    'version': '16.0.1.0.0',
    'category': 'Contracts',
    'summary': 'Module to calculate end of service benefits as per Saudi labor law',
    'depends': ['base', 'hr_contract'],
    'data': [
        'views/eos_service_end_views.xml',
        'reports/eos_service_end_report.xml',
    ],
    'installable': True,
    'application': False,
}
