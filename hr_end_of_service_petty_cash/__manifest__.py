# -*- coding: utf-8 -*-
{
    'name': "HR End Of Service Petty Cash",
    'summary': """HR End Of Service  Petty Cash""",
    'author': "Crevisoft Corporate",
    'website': "https://www.crevisoft.com",

    'category': 'Human Resources',
    'version': '0.1',

    'depends': ['hr_end_of_service', 'petty_cash'],

    # always loaded
    'data': [
        'views/hr_end_service_views.xml',
    ]
}
