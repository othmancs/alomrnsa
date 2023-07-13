# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID


class ProductKit(models.Model):
	_name = 'product.kit'
	_description = "Product Kit"
	
	product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
	qty_uom = fields.Float(string='Quantity', required=True, default=1.0)
	bi_product_template = fields.Many2one(comodel_name='product.template', string='Product pack')
	bi_cost = fields.Float(related='product_id.standard_price', string='Cost', store=True)
	bi_list_price = fields.Float(related='product_id.list_price', string='Public Price', store=True)
	price = fields.Float(related='product_id.lst_price', string='Product Price')
	uom_id = fields.Many2one(related='product_id.uom_id' , string="Unit of Measure", readonly="1")
	name = fields.Char(related='product_id.name', readonly="1")


class ProductProduct(models.Model):
	_inherit = 'product.template'

	is_kit = fields.Boolean(string='Use as Kit')
	cal_kit_price = fields.Boolean(string='Calculate Kit Price')
	kit_ids = fields.One2many(comodel_name='product.kit', inverse_name='bi_product_template', string='Product pack')

	@api.model
	def create(self,vals):
		total = 0
		res = super(ProductProduct,self).create(vals)
		if res.cal_kit_price:
			if 'kit_ids' in vals or 'cal_kit_price' in vals:
					for pack_product in res.kit_ids:
							qty = pack_product.qty_uom
							price = pack_product.product_id.list_price
							total += qty * price
		if total > 0:
			res.list_price = total
		return res


	def write(self,vals):
		total = 0
		res = super(ProductProduct, self).write(vals)
		for pk in self:
			if pk.cal_kit_price:
				if 'kit_ids' in vals or 'cal_kit_price' in vals:
					for pack_product in pk.kit_ids:
						qty = pack_product.qty_uom
						price = pack_product.product_id.list_price
						total += qty * price

		if total > 0:
			self.list_price = total
		return res





class StockPickingInherit(models.Model):
	_inherit = 'stock.picking'
   

class StockMoveInherit(models.Model):
	_inherit = 'stock.move'

	pack_id = fields.Many2one('product.kit',string="Kit")
	

class StockMoveLineInherit(models.Model):
	_inherit = 'stock.move.line'

	pack_id = fields.Many2one('product.kit',string="Kit") 


