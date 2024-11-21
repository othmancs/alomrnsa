{
    'name': 'Restrict Operation Lines',
    'version': '16.0.1.0.0',
    'summary': 'Restrict adding lines to operations without proper access rights',
    'description': """
        Prevent users from adding operation lines in warehouse operations unless they have specific permissions.
    """,
    'author': 'Othmancs92',
    'category': 'Warehouse',
    'depends': ['stock'],
    'data': [
        # 'security/restrict_operation_lines_security.xml',
        # 'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
