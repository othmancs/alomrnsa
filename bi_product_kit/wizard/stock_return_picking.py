# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round




class StockReturnInherit(models.TransientModel):
	_inherit = 'stock.return.picking'


	def create_returns(self):
		obj = self.env['stock.picking'].browse(self._context.get('active_id'))
		if len(obj.move_ids_without_package) != len(self.product_return_moves):
			raise UserError(_("Please, return all kit products."))
		return super().create_returns()
