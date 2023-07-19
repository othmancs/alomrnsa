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

from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime, timedelta
import datetime
from datetime import datetime
from dateutil import relativedelta


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    warehouse_quantity = fields.Char('Stock Quantity per Warehouse')

    @api.onchange('product_id')
    def product_id_change(self):
        # super(SaleOrderLine, self).product_id_change()
        result = {}
        for record in self:
            warehouse = self._write_warehouse_quantity()
            if warehouse:
                record.warehouse_quantity = warehouse

    def _write_warehouse_quantity(self):
        warehouse_quantity_text = ''
        quant_ids = self.env['stock.quant'].sudo().search([('product_id','=',self.product_id.id),('location_id.usage','=','internal')])
        t_warehouses = {}
        for quant in quant_ids:
            if quant.location_id:
                if quant.location_id not in t_warehouses:
                    t_warehouses.update({quant.location_id:0})
                t_warehouses[quant.location_id] += quant.quantity

        tt_warehouses = {}
        for location in t_warehouses:
            warehouse = False
            location1 = location
            while (not warehouse and location1):
                warehouse_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id','=',location1.id)])
                if len(warehouse_id) > 0:
                    warehouse = True
                else:
                    warehouse = False
                location1 = location1.location_id
            if warehouse_id:
                if warehouse_id.name not in tt_warehouses:
                    tt_warehouses.update({warehouse_id.name:0})
                tt_warehouses[warehouse_id.name] += t_warehouses[location]

        for item in tt_warehouses:
            if tt_warehouses[item] != 0:
                warehouse_quantity_text = warehouse_quantity_text + ' ** ' + item + ': ' + str(tt_warehouses[item])
        return warehouse_quantity_text

