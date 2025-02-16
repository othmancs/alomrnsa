# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<https://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL-3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL-3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL-3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'iWesabe Contacts Sequence Number',
    'version': '16.0.0',
    'author': 'iWesabe',
    'summary': 'This module is used to create partner code for customer based on industry field',
    'description': """  """,
    'website': 'https://www.iwesabe.com/',
    'license': 'LGPL-3',

    'depends': [
                'base','contacts'
                ],

    'data': [

        'views/contacts_custom_view.xml',
        'views/partner_industry.xml',
    ],

    'qweb': [],
    'images': ['static/description/iWesabe-Apps-Customer_Number.jpg'],

    'installable': True,
    'application': True,
    'auto_install': False,
}
