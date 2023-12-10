# -*- coding: utf-8 -*-
from odoo import models, fields, api

def get_default_scan_locations(self):
    return bool(self.env['ir.config_parameter'].sudo().get_param('clv_api.clv_default_scan_locations'))

class StockPicking(models.Model):
    """
    Extends stiock.picking class to add settings
    """
    _inherit = 'stock.picking'

    scan_locations = fields.Boolean(string="Scan locations", default=get_default_scan_locations)



