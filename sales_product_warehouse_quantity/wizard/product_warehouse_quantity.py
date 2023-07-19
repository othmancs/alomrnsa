# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2022-Today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import models, fields, api, exceptions
from odoo.tools.translate import _

#from openerp import models, fields, api, exceptions
#from openerp.tools.translate import _

class SaleProductWarehouseQuantity(models.TransientModel):
    _name = "sale.product.warehouse.quantity"
    _description = "Sales Product Warehouse Quantity"

    def _default_warehouse_quantity(self):
        if self.env.context.get('active_model', '') == 'sale.order.line':
            ids = self.env.context['active_ids']
            order_lines = self.env['sale.order.line'].browse(ids)
            if order_lines:
                for line in order_lines:
                    warehouse_quantity = line.warehouse_quantity
                    return warehouse_quantity

    warehouse_quantity = fields.Char(string = 'Stock Quantity per Warehouse', default=_default_warehouse_quantity, required=True, readonly=True)

