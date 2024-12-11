# -*- coding: utf-8 -*-
{
    'name': "HR Side Notes",

    'summary': """Side Note For Employee""",

    'description': """
        Side Note For Employee
    """,
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_side_notes.xml',
        'data/types_data.xml',
    ]
}
