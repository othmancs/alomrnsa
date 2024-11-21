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
    'name': 'Enterprise Overtime update',
    'version': '16.0.2.0.0',
    'summary': 'Manage Employee Overtime',
    'description': """
        Helps you to manage Employee Overtime.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Abdulhadi",
    # 'live_test_url': 'https://youtu.be/lOQCTCxrUKs',
    # 'company': 'Cybrosys Techno Solutions',
    # 'maintainer': 'Cybrosys Techno Solutions',
    # 'website': "https://www.openhrms.com",
    'depends': [
        'hr', 'hr_contract', 'hr_attendance', 'hr_holidays', 'project', 'hr_payroll',
    ],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'data': [

        'data/e_data.xml',
        'views/e_overtime_request_view.xml',
        'views/e_overtime_type.xml',
        'views/e_hr_contract.xml',
        'views/e_hr_payslip.xml',
        'views/custom_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': ['data/e_hr_overtime_demo.xml'],
    'images': ['static/description/hiclipart.com(1).png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
