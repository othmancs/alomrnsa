{
    'name': "Auto Create Contacts from Employees",
    'version': '16.0.1.0.0',
    'summary': "Automatically creates partner contacts for employees",
    'description': """
        This module automatically creates a partner contact for each employee
        and links them together.
    """,
    'author': "Your Name",
    'website': "https://yourwebsite.com",
    'category': 'Human Resources',
    'depends': ['hr', 'contacts'],  # يعتمد على موديول الموظفين وجهات الاتصال
    'data': [],  # يمكنك إضافة ملفات XML/CSV هنا لاحقًا
    'post_init_hook': 'create_contacts_for_existing_employees',  # تشغيل السكربت بعد التثبيت
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}