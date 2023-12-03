{
    'name': 'Custody Management',
    'version': '15.0',
    'summary': """Manage the company properties when it is in the custody of an employee""",
    'description': """First you need to go to employee settings to select source,destination and operation type
    after that go to products screen from custody app to choose which products to be available in custody by
    activate is property choice then go to user groups to select 'custody transfer' to specify the stock users that can
    manage internal transfer""",
    'category': 'Generic Modules/Human Resources',
    'author': "Neoteric Hub",
    'company': 'Neoteric Hub',
    'website': "https://neoterichub.odoo.com",
    'depends': ['mail', 'product', 'stock', 'project', 'purchase', 'documents_hr_recruitment'],
    'data': [
        'security/custody_security.xml',
        'security/ir.model.access.csv',
        'views/wizard_reason_view.xml',
        'views/updation_config.xml',
        'views/custody_view.xml',
        'views/hr_job.xml',
        'views/hr_custody_notification.xml',
        'views/hr_employee_view.xml',
        'views/notification_mail.xml',
        'views/product_product_views.xml',
        'views/purchase_order.xml',
        'views/stock_picking.xml',
        'views/stock_quant.xml',
    ],
    'images': ['static/description/banner.gif'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
