# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{
    'name': 'Archive and Unarchive For Sales, Purchase, Invoice and Stock Transfers',
    'version': '16.0.0.0',
    'category': 'Extra Addons',
    "license": "OPL-1",
    'summary': 'This Application will help you to archive and Unarchive multiple records at a time for sales, purchase, Invoice and Stock. sales order multiple archive and unarchive. Purchase order multiple archive and unarchive. Invoices multiple archive and unarchive. delivery orders multiple archive and unarchive. Incoming order multiple archive and unarchive. stocks records multiple archive and unarchive ',
    'description': """
    This Application will help you to archive and Unarchive multiple records at a time for sales, purchase, Invoice and Stock. 
    sales order multiple records archive and unarchive.
    Purchase order multiple records archive and unarchive.
    Invoices multiple records archive and unarchive.
    delivery orders multiple records archive and unarchive.
    Incoming order multiple records archive and unarchive.
    stocks records multiple records archive and unarchive
    
    sales order single record archive and unarchive.
    Purchase order single record archive and unarchive.
    Invoices single record archive and unarchive.
    delivery orders single record archive and unarchive.
    Incoming order single record archive and unarchive.
    stocks single record archive and unarchive 
    
    Filter archived records in sales order
    Filter archived records in sales quotation
    Filter archived records in purchase order
    Filter archived records in stock transfer order
    Filter archived records in invoices
    
    sales order multiple records Active and Inactive.
    Purchase order multiple records Active and Inactive.
    Invoices multiple records Active and Inactive.
    delivery orders multiple records Active and Inactive.
    Incoming order multiple records Active and Inactive.
    stocks records multiple records Active and Inactive
    
    Hide and show sales orders
    Hide and show purchase orders
    Hide and show Invoices
    Hide and show bills
    Hide and show stock transfer
    inherit sale.order
    inherit purchase.order
    inherit account.move
    inherit stock.transfer
    
    
""",
    "price": 0,
    "currency": 'EUR',
    'author': 'Sitaram',
    'depends': ['base','stock','sale_management','account','purchase'],
    'data': [
             'views/sr_inherit_sale_order.xml',
             'views/sr_inherit_invoice.xml',
             'views/sr_inherit_purchase_order.xml',
             'views/sr_inherit_stock.xml',
    ],
    'website':'https://sitaramsolutions.in',
    'installable': True,
    'auto_install': False,
    'live_test_url':'www.sitaramsolutions.in',
    "images":['static/description/banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
