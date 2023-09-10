# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-Today Ascetic Business Solution <www.asceticbs.com>
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

from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_order_type = fields.Many2one('sale.type', string="Sale Order Type")

class SaleOrder(models.Model):
    _inherit = "sale.order"

    #This function is automatically fill customers sale order types field on sale order.  
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        result = super(SaleOrder, self).onchange_partner_id()
        for record in self:
            if record.partner_id:
                partner_sale_order_type = record.partner_id.sale_order_type
                record.payment_term_id = partner_sale_order_type.payment_term_id
                record.warehouse_id = partner_sale_order_type.warehouse_id
                record.incoterm = partner_sale_order_type.incoterm
                record.picking_policy = partner_sale_order_type.picking_policy
                record.user_id = partner_sale_order_type.user_id
                record.tag_ids = partner_sale_order_type.tag_ids
                record.team_id = partner_sale_order_type.team_id
                record.client_order_ref = partner_sale_order_type.client_order_ref
                record.origin = partner_sale_order_type.origin
                record.campaign_id = partner_sale_order_type.campaign_id
                record.medium_id = partner_sale_order_type.medium_id
                record.source_id = partner_sale_order_type.source_id
                record.opportunity_id = partner_sale_order_type.opportunity_id
            return result

