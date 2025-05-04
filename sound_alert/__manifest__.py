{
    'name': 'Voice & Sound Alert Notification',
    'version': '16.0.1.0',

    'summary': 'Let your Odoo system speak — Stay informed without staring at your screen.',
    'description': 'Sound and Voice Notification & Alerts for Odoo.',

    'category': 'tools',
    'author': 'Lighthouse',
    'maintainer': 'Ashuty',
    'support': 'lighthouse.aashuty@outlook.com',
    'website': '',
    'license': 'OPL-1',

    'depends': ['base', 'web', 'base_setup', 'bus', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/sound_alert_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'sound_alert/static/src/js/alert_sound.js',
            'sound_alert/static/src/css/main.css'
        ]
    },
    'external_dependencies': {
        'python': ['gTTS'],
    },
    'demo': [
        'demo/demo.xml'
    ],

'images': ['static/description/banner.png'],

    'installable': True,
    'auto_install': False,
    'application': True,
}
