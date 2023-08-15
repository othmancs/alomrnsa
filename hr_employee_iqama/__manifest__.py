# -*- coding: utf-8 -*-

{
    'name': 'Employee IQAMA Management KSA',
    'version': '15.0.0.1',
    'summary': """Manage employee iqama. Especially For Saudi Arabia. K.S.A
                إقامة موظف في المملكة العربية السعودية
    """,
    'description': """Manage employee iqama. Especially For Saudi Arabia. K.S.A""",
    'category': 'Human Resources',
    'author': 'bisolv',
    'website': "",
    'license': 'AGPL-3',

    'price': 16,
    'currency': 'USD',

    'depends': ['hr', 'hijri_islamic_calendar'],

    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
        'views/hr_employee_iqama_view.xml',
        'views/hr_employee_dashboard_view.xml',

    ],
    'demo': [

    ],
    'images': ['static/description/banner.png'],
    'qweb': [],

    'installable': True,
    'auto_install': False,
    'application': False,
}
