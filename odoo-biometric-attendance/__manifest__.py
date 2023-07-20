# -*- coding: utf-8 -*-
{
    'name': "Zkteco, eSSL, Cams Biometrics Integration Module with HR Attendance",
    'summary': """Receives the attendance/punches from the biometric devices and updates in hr.attendance module of odoo server.""",
    'description': """
        The module is developed based on the Cams biometric web api as documented at https://camsunit.com/application/biometric-web-api.html. It receives the biometric attendance on realtime and integrates with hr.attendance module. 
        
	It supports all the cams biometrics machines listed at https://camsunit.com/product/home.html
        It alos supports 
        	ZKTeco, 
        	eSSL, 
        	Identix, 
        	BioMax 
        	and more biometric machines provided they are verified at https://developer.camsunit.com/
        
        Module requires valid API license as listed at https://camsunit.com/application/biometric-web-api.html#api_cost
        
    """,

    'author': "Cams Biometrics",
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'license': 'AGPL-3',
    'company': 'Cams Biometrics',
    'website': "https://www.camsunit.com",
    'depends': ['hr','hr_attendance'],
    'installable': True,
    'images':[
        'static/description/banner.png',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/config.xml',
        'views/inherited_employee_view.xml',
    ]
}
