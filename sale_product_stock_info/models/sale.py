# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def action_show_line_product_stock(self):
        stock_warehouse_obj = self.env['stock.warehouse']
        stock_location_obj = self.env['stock.location']
        orderline_product_stock_info_line_obj = self.env['orderline.product.stock.info.line']
        ir_config = self.env['ir.config_parameter'].sudo().get_param('sale_product_stock_info.order_line_stock_type')
        if not ir_config:
            raise UserError(_("Please first configure Stock Type(Warehouse / Location Wise) option inside "
                              "Setting -> Sale -> Show Stock Info. in Order Line? then you can see the Stock Info."))

        stock_info_wizard_id = self.env['orderline.product.stock.info'].create({'product_id': self.product_id.id})
        if ir_config == 'warehouse_wise':
            for warehouse_id in stock_warehouse_obj.search([]):
                data = self.product_id.with_context(to_date=fields.Datetime.now(), warehouse=warehouse_id.id).read([
                    'qty_available', 'incoming_qty', 'outgoing_qty', 'virtual_available', 'free_qty', ])
                orderline_product_stock_info_line_obj.create({
                    'orderline_product_stock_info_id': stock_info_wizard_id.id,
                    'warehouse_id': warehouse_id.id,
                    'location_id': False,
                    'qty_available': data and data[0].get('qty_available') or 0,
                    'incoming_qty': data and data[0].get('incoming_qty') or 0,
                    'outgoing_qty': data and data[0].get('outgoing_qty') or 0,
                    'virtual_available': data and data[0].get('virtual_available') or 0,
                    'free_qty': data and data[0].get('free_qty') or 0,
                })
        elif ir_config == 'location_wise':
            quant_locations = self.env['stock.quant'].search(
                [('product_id', '=', self.product_id.id), ("on_hand", "=", True)]).mapped("location_id").filtered(
                lambda x: x.usage == "internal")
            for location in quant_locations:
                data = self.product_id.with_context(to_date=fields.Datetime.now(), location=location.id).read([
                    'qty_available', 'free_qty', 'virtual_available', ])
                warehouse_id = location.warehouse_id and location.warehouse_id.id or False
                orderline_product_stock_info_line_obj.create({
                    'orderline_product_stock_info_id': stock_info_wizard_id.id,
                    'warehouse_id': warehouse_id,
                    'location_id': location.id,
                    'qty_available': data and data[0].get('qty_available') or 0,
                    'incoming_qty': data and data[0].get('incoming_qty') or 0,
                    'outgoing_qty': data and data[0].get('outgoing_qty') or 0,
                    'virtual_available': data and data[0].get('virtual_available') or 0,
                    'free_qty': data and data[0].get('free_qty') or 0,
                })

        view = self.env.ref("sale_product_stock_info.orderline_product_stock_info_form_view")
        return {
            'name': self.product_id.name,
            'views': [(view.id, "form")],
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': stock_info_wizard_id.id,
            'res_model': 'orderline.product.stock.info',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'edit': False},
        }
