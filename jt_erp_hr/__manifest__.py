# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2019-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'ERP HR Addon',
    'summary': 'Install HR modules package in single click',
    'version': '16.0.1.0',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': 'http://www.jupical.com',
    'license': 'AGPL-3',
    'depends': [
        'hr', 'hr_attendance', 'hr_contract', 'hr_expense',
        'hr_fleet', 'hr_gamification', 'hr_holidays', 
        'hr_holidays_attendance', 'hr_maintenance',
        'hr_org_chart', 'hr_presence', 'hr_recruitment',
        'hr_recruitment_survey', 'hr_skills', 'hr_skills_slides',
        'hr_skills_survey', 'hr_timesheet', 'hr_timesheet_attendance',
        'hr_work_entry', 'website_hr_recruitment',
    ],
    'images': [
        'static/description/poster_image.png'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
