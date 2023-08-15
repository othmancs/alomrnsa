# -*- coding: utf-8 -*-
{
    'name': 'Hijri Calendar Date Widget',
    'version': '15.0.0.1',
    'summary': """
        Hijri Islamic Calendar Date Picker Widget. Using Saudi (KSA), UAE other gulf countries.
 
    """,
    'description': """Hijri Islamic Date Picker Widget""",
    'category': 'Extra Tools',
    'author': 'bisolv',
    'website': "www.bisolv.com",
    'license': 'AGPL-3',

    'price': 19.0,
    'currency': 'USD',

    'depends': ['base'],

    'data': [],

    'assets': {

        'web.assets_backend': [
            '/hijri_islamic_calendar/static/src/js/widget.js',
            '/hijri_islamic_calendar/static/src/xml/widget.xml',
        ],
    },

    'demo': [

    ],
    'images': ['static/description/banner.png'],
    'qweb': [],

    'installable': True,
    'auto_install': False,
    'application': False,
}


