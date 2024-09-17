# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import fields, models


class srStockPicking(models.Model):
    _inherit = 'stock.picking'
    
    active = fields.Boolean('Active', default=True)

