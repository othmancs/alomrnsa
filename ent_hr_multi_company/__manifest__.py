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
    'name': 'Enterprise Open HRMS Multi-Company',
    'version': '16.0.1.0.1',
    'summary': """Enables Multi-Company""",
    'description': 'This module enables multi company features',
    'category': 'Generic Modules/Human Resources',
    'author': "Cybrosys Techno Solutions,Open HRMS",
    'company': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'maintainer': 'Cybrosys Techno Solutions',
    'depends': ['base', 'hr','hr_contract', 'hr_payroll', 'hr_expense', 'hr_attendance','hr_holidays'],
    'data': [
        'views/hr_company_view.xml',
        'views/multi_company_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
