# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Users(models.Model):
    _inherit = 'res.users'

    stock_type_ids = fields.Many2many(comodel_name="stock.picking.type", string="Allowed Stock Types", )


class StockType(models.Model):
    _inherit = 'stock.picking.type'

    user_ids = fields.Many2many(comodel_name="res.users", string="Users", )
    current_user_id = fields.Many2one('res.users', compute='_compute_current_user', string='Current User')

    def _compute_current_user(self):
        for record in self:
            record.current_user_id = self.env.user
