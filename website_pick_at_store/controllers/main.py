# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery
from odoo.http import request


class WebsiteSaleDeliveryStorePickup(WebsiteSaleDelivery):

    def _get_shop_payment_values(self, order, **kwargs):
        values = super()._get_shop_payment_values(order, **kwargs)
        if order.carrier_id and order.carrier_id.personal_store_pickup:
            warehouses = order.carrier_id.get_available_stores(order)
            if not warehouses:
                values['errors'].append(
                    (_('Sorry, we are unable to ship your order'),
                    _('No store is available for your current order. '
                    'Please contact us for more information.')))
            values['warehouses'] = warehouses
        return values

    @http.route(['/shop/update_pickup_warehouse'], type='json', auth="public",
        methods=['POST'], website=True, csrf=False)
    def update_pickup_warehouse(self, **post):
        order = request.website.sale_get_order()
        warehouse_id = int(post['warehouse_id'])
        res = {}
        self.do_update_pickup_warehouse(order, warehouse_id)
        return res

    def do_update_pickup_warehouse(self, order, warehouse_id):
        if warehouse_id and warehouse_id != order.warehouse_id.id:
            warehouse = request.env['stock.warehouse'].sudo().browse(
                warehouse_id)
            order.warehouse_id = warehouse
            if warehouse.partner_id:
                order.store_address_id = warehouse.partner_id

    @http.route(['/shop/update_carrier'], type='json', auth='public',
                methods=['POST'], website=True, csrf=False)
    def update_eshop_carrier(self, **post):
        result = super().update_eshop_carrier(**post)
        order = request.website.sale_get_order()
        carrier = request.env['delivery.carrier'].sudo().browse(
            int(post.get('carrier_id')))
        warehouses = []
        if carrier.personal_store_pickup:
            warehouses = carrier.get_available_stores(order)
            if warehouses:  # Set default store
                self.do_update_pickup_warehouse(order, warehouses[0]['id'])
        else:
            order.store_address_id = False
            order_warehouse_id = order._get_warehouse_available()
            if order_warehouse_id != order.warehouse_id.id:
                order.warehouse_id = \
                    request.env["stock.warehouse"].browse(order_warehouse_id)

        result.update({
            'personal_store_pickup': carrier.personal_store_pickup,
            'warehouses': warehouses,
            'warehouse': warehouses and warehouses[0] or {},
            'warehouse_id': order.warehouse_id.id
        })
        return result
