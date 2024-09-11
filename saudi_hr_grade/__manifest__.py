# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "HR Grade",
    'summary': """ HR Grade""",
    'description': """
        Job position wise Employee Grading details.""",
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_grade_view.xml',
    ],
    'price': 10,
    'currency': 'EUR',
    'demo': ['demo/demo.xml'],
    'images': [
        'static/description/main_screen.png'
    ],
    'installable': True,
    'auto_install': False,
}
