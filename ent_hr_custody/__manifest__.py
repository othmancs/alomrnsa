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
    'name': 'Enterprise Open HRMS Custody',
    'version': '16.0.1.0.0',
    'summary': """Manage the company properties when it is in the custody of an employee""",
    'description': 'Manage the company properties when it is in the custody of an employee',
    'live_test_url': 'https://www.youtube.com/watch?v=keh3ttj9kws&feature=youtu.be',
    'category': 'Generic Modules/Human Resources',
    'author': "Cybrosys Techno Solutions,Open HRMS",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr', 'mail', 'ent_hr_employee_updation', 'product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/custody_security.xml',
        'views/wizard_reason_view.xml',
        'views/custody_view.xml',
        'views/hr_custody_notification.xml',
        'views/hr_employee_view.xml',
        'data/mail_template_data.xml',
        'reports/custody_report.xml'
    ],
    'demo': ['data/demo_data.xml'],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
