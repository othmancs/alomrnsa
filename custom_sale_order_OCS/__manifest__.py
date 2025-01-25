{
    'name': 'My Custom Module Othmancs',
    'version': '16.0.1.0.0',
    'summary': 'Custom module to add pricelist_item_id to sale.order.line',
    'description': 'This module adds a custom field pricelist_item_id to sale.order.line model.',
    'category': 'Sales',
    'author': 'othmancs',
    'website': 'https://othmancs.com',
    'depends': ['sale'],  # يعتمد على موديول Sale
    'data': [
        'views/sale_order_line_views.xml',  # إضافة واجهة المستخدم
    ],
    'installable': True,
    'application': True,
}