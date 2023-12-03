# -*- coding: utf-8 -*-
{
    'name': "Etimad CRM Automation",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Barameg",
    'website': "https://barameg.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'CRM',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/views.xml',
        'views/res_config_settings.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/Etimad_logo.png',
    ],
}
