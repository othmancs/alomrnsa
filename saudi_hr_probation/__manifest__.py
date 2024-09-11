# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "HR Employee Probation",
    'summary': """ HR Employee Probation """,
    'description': """
        HR Employee Probation details
        Employee Probation Plan.
        Employee Review.
        Automatically Set Stage From 'probation' to 'employee' when probation period is completed.
        Pre Design Editable Mail Templates.
        Managing employee's different stages.
        Employee's current stage in tree view.
        Employee's current stage in kanban view.
        Group by stage in search view.
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['hr_recruitment', 'saudi_hr_contract'],#, 'saudi_hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/email_template_view.xml',
        'data/cron.xml',
        'views/res_config_settings_view.xml',
        'views/hr_department_view.xml',
        'views/hr_employee_probation_view.xml',
        'views/hr_employee_view.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml'
    ],
    'images': [
        'static/description/main_screen.png'
    ],
    "price": 80.0,
    "currency": "EUR",
    'installable': True,
    'auto_install': False,
}
