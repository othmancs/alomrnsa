# -*- coding: utf-8 -*-
{
    'name': "Hr Calculate Request22",
    'version': '16.0.1',
    'summary': 'Hr Calculate Request22',
    'sequence': 12,
    'description': """Hr Calculate Request""",
    'category': 'Accounting',
    'license': 'AGPL-3',
    'depends': ['base', 'hr','hr_contract','hr_payroll'],
    'data': [
        'views/report_end_of_service.xml',
        'report/report_end_of_service_template.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
