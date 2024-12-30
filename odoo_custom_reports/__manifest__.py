# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

{
    'name': "Odoo Custom Reports",
    'author': 'SIMI Technologies',
    'category': 'reports',
    'summary': """ Cutom PDF and Excel Reports """,
    'website': 'http://www.simitechnologies.co.ke',
    'license': 'AGPL-3',
    'description': """
""",
    'version': '16.0.1.0',
    # 'price': 59.99,
    'currency': 'EUR',
    'depends': ['base','account', 'report_xlsx'],
    'data': ['security/ir.model.access.csv',
             'wizard/product_invoice.xml',
             'views/product_invoice_report_view.xml',
             'report/product_invoice_template.xml',
             'report/product_invoice_report.xml',
             ],
    'installable': True,
    'images': ['static/description/banner.png'],
    'application': True,
    'auto_install': False,
}
