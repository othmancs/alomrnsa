# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Adjustment(models.Model):
    _inherit = 'stock.inventory'


class Location(models.Model):
    _inherit = 'stock.location'

    adj_seq = fields.Integer(string="Adjustment Next Sequence", required=False, default=1)


