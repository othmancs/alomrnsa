# -*- coding: utf-8 -*-
{
    'name': "Employee Expenses Workspace - Self Service",
    'summary': """
        Self-Service Expense Management
    """,
    'description': """
        The Self-Service Expense Management sub-module within the employee workspace in Odoo empowers users to efficiently manage their expenses. Employees can easily submit expense claims, attaching receipts and categorizing expenses. They can also track the approval status of their claims and access a detailed history of past reimbursements. This feature streamlines the expense reimbursement process, allowing employees to take charge of their financial transactions and enhancing transparency in expense management within the organization.
    """,
    'author': 'Dynexcel',
    'website': 'https://www.dynexcel.com',
    'version': '0.1',
    'category': 'Human Resources',
    'depends': ['de_hr_workspace','hr_expense'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_expense_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
