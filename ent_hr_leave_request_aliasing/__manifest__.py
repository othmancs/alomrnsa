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
    'name': 'Enterprise Open HRMS Leave Request Aliasing',
    'version': '16.0.1.0.0',
    'summary': """Allows You To Create Leave Request Automatically From Incoming Mails""",
    'description': 'This module allows you to create leave request directly from incoming mails.',
    'live_test_url': 'https://youtu.be/jQFAP20k_Wc',
    'category': 'Generic Modules/Human Resources',
    'author': "Cybrosys Techno Solutions,Open HRMS",
    'company': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'maintainer': 'Cybrosys Techno Solutions',
    'depends': ['base', 'base_setup', 'hr', 'hr_holidays'],

    'data': [
        'views/leave_request_alias_view.xml',
        'views/res_config_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ent_hr_leave_request_aliasing/static/src/js/web_planner_hr_leave.js',
            ],
    },
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
