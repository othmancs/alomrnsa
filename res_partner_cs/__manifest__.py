# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Customer Type Extension',
    'version': '1.0',
    'summary': 'Add customer type field to contacts',
    'description': 'This module adds a customer type field (Cash or Credit) to contacts and restricts the creation of Credit customers based on user permissions.',
    'author': 'Your Name',
    'depends': ['contacts'],
    'data': [
        'security/customer_type_security.xml',
        'security/ir.model.access.csv', 
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
}
