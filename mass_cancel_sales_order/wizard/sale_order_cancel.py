# -*- coding: utf-8 -*-
from odoo import models


class SaleOrderCancel(models.TransientModel):
    _name = "sale.order.cancel"
    _description = "Sales Order Cancel"

    def cancel_order(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        sale_orders.write({'state': 'cancel'})
        return sale_orders
