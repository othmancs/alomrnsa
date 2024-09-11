# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'IT Operations',
    'category': 'Human Resources',
    'description': """
    > Software and Hardware request with demage control and expense
    > Employee Registrations
    > Employee De-registrations
    > Employee Excess Card, Visiting Card Templates
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'version': '1.4',
    'sequence': 20,
    'license': 'OPL-1',
    'depends': [
        'base', 'stock', 'hr_expense_payment', 'saudi_hr', 'hr_maintenance'
    ],
    'data': [
        'data/it_product_data.xml',
        'data/ir_sequence.xml',
        'data/report_layout.xml',
        'report/equipment_form_report.xml',
        'report/hr_agreement_form_view.xml',
        'report/print_qr_label_report.xml',
        'report/print_qr_double_report.xml',
        'data/mail_template_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        # 'views/hr_it_operations.xml',
        'views/hr_employee_registration_view.xml',
        # 'views/hr_employee_deregistration_view.xml',
        'views/maintenance_views.xml',
        'views/hr_expense_view.xml',
        'views/equipment_request_view.xml',
        'views/product_view.xml',
        'views/hr_employee_view.xml',
        'views/emp_exit_procedure.xml',
        'wizard/print_qr_label_view.xml',
        'wizard/emp_exit_report_template.xml',
        'wizard/emp_exit_report_view.xml',
        'wizard/emp_equipment_fields_wizard_view.xml',
        'menu.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'saudi_hr_it_operations/static/src/js/barcode_widget.js',
            'saudi_hr_it_operations/static/src/js/form_view.js',
        ]
    },
    'demo': [
        'data/equipment_registration_data.xml',
        'demo/equipment_request_demo.xml',
        'demo/employee_registration_demo.xml',
    ],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
