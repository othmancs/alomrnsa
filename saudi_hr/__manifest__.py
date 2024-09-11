# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Human Resource",
    'summary': """ Human Resource Management """,
    'description': """
        Human Resource Management specific for companies
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'Human Resources/Employee',
    'version': '16.1.2',
    'license': 'OPL-1',
    'sequence': 20,
    'depends': ['saudi_hr_groups_configuration', 'hr_fiscal_year', 'website', 'phone_validation', 'contacts'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        'data/employee_category_data.xml',
        'data/mail_channel_demo.xml',
        'data/birthday_template.xml',
        'data/birthday_cron.xml',
        'views/personal_locker_view.xml',
        'views/web_template.xml',
        'views/res_config_view.xml',
        'views/hr_view.xml',
        'views/education.xml',
        'reports/active_employee.xml',
        'wizard/employee_head_count_report_view.xml',
        'wizard/employee_head_count_report_template.xml',
        'wizard/new_joining_report_view.xml',
        'wizard/new_joining_report_template.xml',
        'wizard/employee_active_list_report.xml',
        'wizard/employee_active_list.xml',
        'wizard/birthday_list_template.xml',
        'wizard/emp_birthday_list.xml',
        'wizard/import_employee_view.xml',
        'views/web_employee_directory_template.xml',
        'views/email_template_view.xml',
        'views/cron.xml',
        'menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'saudi_hr/static/src/js/form_view.js',
            'saudi_hr/static/src/scss/search_panel.scss'
        ],
        'web.assets_frontend': [
            'saudi_hr/static/src/scss/style.scss',
            # 'saudi_hr/static/src/js/employee_private_info.js'
        ],
    },
    'demo': [
        # 'demo/user_demo.xml',
        # 'demo/demo.xml',
        # 'demo/group_configuration_demo.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
