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
    'name': 'Enterprise Open HRMS Advance Salary',
    'version': '16.0.1.0.0',
    'summary': 'Advance Salary In HR',
    'description': """
        Helps you to manage Advance Salary Request of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'live_test_url': 'https://youtu.be/fJ3RyE7RGz4',
    'author': "Cybrosys Techno Solutions,Open HRMS",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': [
        'ent_hr_payroll_extension', 'hr_payroll', 'hr', 'account_accountant', 'hr_contract', 'ent_ohrms_loan',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/salary_structure.xml',
        'security/security.xml',
        'views/salary_advance.xml',

    ],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}

