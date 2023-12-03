# -*- coding: utf-8 -*-
{
    'name': "Employee Workspace",
    'version': '0.1',
    'category': 'Human Resources',
    'summary': """
        Odoo HR Module: Empowering Employee Self-Service
        """,
    'description': """
        The "HR" module in Odoo is designed with a strong focus on empowering employees through self-service capabilities. It serves as a centralized platform for employees to manage their own HR-related tasks and information. Within this module, employees can effortlessly request and track their leaves, log attendance, and access personal details. This self-service approach streamlines administrative processes, enabling employees to take more control over their HR needs. It also includes features like timesheet management and performance appraisals, allowing employees to actively participate in their career development. This module plays a pivotal role in enhancing employee engagement and satisfaction by providing a user-friendly, self-service workspace.
    """,
    'author': 'Dynexcel',
    'website': 'https://www.dynexcel.com',
    'depends': ['base','hr','hr_contract'],
    'data': [
        'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/workspace_menu.xml',
        'views/hr_employee_views.xml',
        'views/hr_contract_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
