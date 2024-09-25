{
    'name': 'ZK Attendance Sync',
    'version': '1.0',
    'summary': 'Integrate ZKTeco devices with Odoo for attendance tracking',
    'description': 'This module integrates ZKTeco biometric devices with Odoo to track employee attendance.',
    'category': 'Human Resources',
    'author': 'Your Name',
    'depends': ['hr', 'hr_attendance'],
    'data': [
        'views/zk_attendance_views.xml',
        'views/zk_device_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
