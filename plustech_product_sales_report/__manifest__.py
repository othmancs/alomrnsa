# -*- coding: utf-8 -*-
#################################################################################
# Author      : Plus Technology Co.Ltd. (<https://www.plustech-it.com//>)
# Copyright(c): 2024-Present Plus Technology Co. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
{
    'name': "Product Sales Report",
    'author': "Plus Tech Company",
    'company': "Plus Tech Company",
    'website': "www.plustech-it.com",
    'category': 'report',
    'version': '16',
    'images': ["static/description/banner.gif"],
    'currency': 'USD',
    'price': '0',
    'license': 'AGPL-3',
    'depends': ['base','account', 'sale','report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/sale_products_report_view.xml',
        'reports/sale_products_report_template.xml',
        'views/sales_product_report_report.xml',
    ],
}
