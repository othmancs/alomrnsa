# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################
{
    'name': 'Enterprise Open HRMS Core',
    'version': '16.0.1.0.0',
    'summary': """Open HRMS Suit: It brings all Open HRMS modules""",
    'description': """Openhrms, Main module of Open HRMS, It brings all others into a single module, Payroll, Payroll Accounting,Expense,
                Dashboard, Employees, Employee Document, Resignation, Salary Advance, Loan Management, Gratuity, Service Request, Gosi, WPS Report, Reminder, Multi Company, Shift Management, Employee History,
                Branch Transfer, Employee Appraisal,Biometric Device, Announcements, Insurance Management, Vacation Management,Employee Appreciations, Asset Custody, Employee Checklist, Entry and Exit Checklist, Disciplinary Actions, openhrms, OpenHRMS, hrms, Attrition Rate, Document Expiry, Visa Expiry, Law Suit Management, Employee, Employee Training""",
    'category': 'Generic Modules/Human Resources',
    'author': "Cybrosys Techno Solutions,Open HRMS",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'live_test_url': 'https://youtu.be/kBBlUFofCTs',
    'website': "https://www.openhrms.com",
    'depends': ['web',
                'hr',
                'hr_payroll_account',
                'hr_gamification',
                'ent_hr_employee_updation',
                'hr_recruitment',
                'hr_attendance',
                'hr_holidays',
                'hr_payroll',
                'hr_expense',
                'ent_hr_leave_request_aliasing',
                'hr_timesheet',
                'ent_oh_employee_creation_from_user',
                'ent_employee_documents_expiry',
                'ent_hr_multi_company',
                'ent_loan_accounting',
                'ent_ohrms_salary_advance',
                'ent_hr_reward_warning',
                'ent_hrms_dashboard',
                'ent_hr_reminder'
                ],
    'data': ['views/menu_arrangement_view.xml'

             ],
    'assets': {
        'web.assets_backend': [

        ],
        'web.assets_qweb': [

        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
