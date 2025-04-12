# -*- coding: utf-8 -*-

{
    'name': 'HR Contract IQAMA Number',
    'version': '16.0.1.0.0',
    'summary': 'Add IQAMA number to employee contract',
    'description': """
        This module adds the employee's IQAMA number to the contract form,
        displayed under the employee field and makes it exportable.
    """,
    'category': 'Human Resources',
    'author': 'Othmancs',
    'website': 'https://www.yourwebsite.com',
    'depends': ['hr_contract'],
    'data': [
        'views/hr_contract_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}