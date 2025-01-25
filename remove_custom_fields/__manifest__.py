{
    'name': 'Remove Custom Fields',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Remove specific custom fields from the database',
    'description': '''
        This module removes the custom fields 'pricelist_item_id' and 
        'x_product_pricelist_item_id' from the database.
    ''',
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'depends': ['base'],
    'data': [],
    # 'post_init_hook': 'remove_custom_fields',
    'installable': True,
    'application': False,
    'auto_install': False,
}
