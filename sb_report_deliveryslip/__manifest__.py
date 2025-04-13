# -*- coding: utf-8 -*-
{
    'name': "sb_report_deliveryslip",
    'version': '0.1',
    'depends': ['base', 'stock', 'sb_mr_driver_shipping_letter'],
    'data': [
        'reports/sb_report_deliveryslip.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'sb_report_deliveryslip/static/src/css/arabic_style.css',
        ],
    },
}
