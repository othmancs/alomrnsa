# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models


class MaterialRequestLine(models.Model):
    _name = "material.request.line"
    _description = "Material Request Lines"

    product_id = fields.Many2one("product.product", string="المنتج", required=True)
    description = fields.Char(string="الوصف", required=True)
    qty = fields.Float(string="الكمية المطلوبة", default=1, required=True)
    product_uom_category_id = fields.Many2one(
        related="product_id.uom_id.category_id", readonly=True
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="وحدة القياس",
        required=True,
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    request_id = fields.Many2one("material.request")

    qty_available = fields.Integer(string='كمية المستقل', compute='_compute_qty_available', store=True)
    qty_available_from = fields.Integer(string='كمية المصدر', compute='_compute_qty_available_from', store=True)

    @api.depends('request_id.location_id', 'product_id')
    def _compute_qty_available(self):
        for rec in self:
            if rec.request_id.state != 'confirm':
                avail_qty = self.env['stock.quant'].search([
                    '|',
                    ('location_id', '=', rec.request_id.location_id.id),
                    ('parent_location_id', '=', rec.request_id.location_id.id),
                    ('product_id', '=', rec.product_id.id)
                ])

                if avail_qty:
                    rec.qty_available = sum(avail_qty.mapped('quantity'))
                else:
                    rec.qty_available = 0

    @api.depends('request_id.dest_location_id', 'product_id')
    def _compute_qty_available_from(self):
        for rec in self:
            if rec.request_id.state != 'confirm':
                avail_qty = self.env['stock.quant'].search([
                    '|',
                    ('location_id', '=', rec.request_id.dest_location_id.id),
                    ('parent_location_id', '=', rec.request_id.dest_location_id.id),
                    ('product_id', '=', rec.product_id.id)
                ])

                if avail_qty:
                    rec.qty_available_from = sum(avail_qty.mapped('quantity'))
                else:
                    rec.qty_available_from = 0

    @api.onchange("product_id")
    def product_id_change(self):
        if self.product_id:
            self.description = self.product_id.name
            self.uom_id = self.product_id.uom_id
