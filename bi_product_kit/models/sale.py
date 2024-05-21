# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################


from odoo import api, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID
from collections import namedtuple, OrderedDict, defaultdict

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	@api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.product_uom_qty', 'move_ids.product_uom')
	def _compute_qty_delivered(self):
		
		super(SaleOrderLine, self)._compute_qty_delivered()

		for line in self:  # TODO: maybe one day, this should be done in SQL for performance sake
			def check_product(x):
				for rec in line.product_id.kit_ids:
					if x == rec.product_id:
						return x
			
			if line.qty_delivered_method == 'stock_move':
				qty = 0.0
				flag = False
				count = 0
				done_list = [] 
				deliver_list = []
				move_list = []
				products = []
				filtered = []
				picking_ids = self.env['stock.picking'].search([('origin','=',line.order_id.name)])
				for pick in picking_ids:
					for move_is in pick.move_ids_without_package:
						if move_is.product_id not in products:
							products.append(move_is.product_id)
				pro = filter(check_product,products)
				for product in pro:
					filtered.append(product)
				for pick in picking_ids:
					for move_is in pick.move_ids_without_package: 
						if move_is.product_id in filtered:
							if move_is.pack_id in line.product_id.kit_ids:
								move_list.append(move_is.product_uom_qty)
								done_list.append(move_is.quantity_done)

				stock_move = self.env['stock.move'].search([('origin','=',line.order_id.name)])
				if line.product_id.is_kit == True:
					list_of_sub_product = []
					for product_item in line.product_id.kit_ids:
						list_of_sub_product.append(product_item.product_id)
					for move in stock_move:
						if count == 0:
							if move.state == 'done' and move.product_uom_qty == move.quantity_done:
								flag = True
								for picking in picking_ids:
									for move_is in picking.move_ids_without_package:
										if sum(move_list) == 0:
											pass
										else: 
											deliver_qty =(line.product_uom_qty*sum(done_list))/sum(move_list)
											line.qty_delivered = int(deliver_qty)
											deliver_list.append(line.qty_delivered)        
										  
							elif move.state == 'confirmed':
								flag = 'confirmed'
								count = count+1
								done_list.append(move.quantity_done)
								for picking in picking_ids:
									for move_is in picking.move_ids_without_package:
										if sum(move_list) == 0:
											pass
										else:
											deliver_qty =(line.product_uom_qty*sum(done_list))/sum(move_list)
											line.qty_delivered = int(deliver_qty)
											deliver_list.append(line.qty_delivered)
				else:
					outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
					for move in outgoing_moves:
						if move.state != 'done':
							continue
						qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
					for move in incoming_moves:
						if move.state != 'done':
							continue
						qty -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
					line.qty_delivered = qty

	@api.onchange('product_id', 'product_uom_qty')
	def _compute_qty_to_deliver(self):
		res = super(SaleOrderLine, self)._compute_qty_to_deliver()
		for i in self:
			if i.product_id.is_kit:
				if i.product_id.type == 'product':
					warning_mess = {}
					for pack_product in i.product_id.kit_ids:
						qty = i.product_uom_qty
						if qty * pack_product.qty_uom > pack_product.product_id.virtual_available:
							warning_mess = {
									'title': _('Not enough inventory!'),
									'message' : ('You plan to sell %s but you only have %s %s available, and the total quantity to sell is %s !' % (qty, pack_product.product_id.virtual_available, pack_product.product_id.name, qty * pack_product.qty_uom))
									}
							return {'warning': warning_mess}
			else:
				return res

	def _action_launch_stock_rule(self, previous_product_uom_qty=False):
		"""
		Launch procurement group run method with required/custom fields genrated by a
		sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
		depending on the sale order line product rule.
		"""
		if self._context.get("skip_procurement"):
			return True
		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
		procurements = []
		errors = []
		for line in self:
			line = line.with_company(line.company_id)
			if line.state != 'sale' or not line.product_id.type in ('consu','product'):
				continue
			qty = line._get_qty_procurement(previous_product_uom_qty)
			if float_compare(qty, line.product_uom_qty, precision_digits=precision) == 0:
				continue

			group_id = line._get_procurement_group()
			if not group_id:
				group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
				line.order_id.procurement_group_id = group_id
			else:
				# In case the procurement group is already created and the order was
				# cancelled, we need to update certain values of the group.
				if line.product_id.kit_ids:
					values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)
					for val in values:
						try:
							pro_id = self.env['product.product'].browse(val.get('product_id'))
							stock_id = self.env['stock.location'].browse(val.get('partner_dest_id'))
							product_uom_obj = self.env['uom.uom'].browse(val.get('product_uom'))
							procurements.append(self.env['procurement.group'].Procurement(
								pro_id, 0, product_uom_obj,
								line.order_id.partner_shipping_id.property_stock_customer,
								val.get('name'), val.get('origin'), line.order_id.company_id, val
							))
						except UserError as error:
							errors.append(error.name)
				else:
					updated_vals = {}
					if group_id.partner_id != line.order_id.partner_shipping_id:
						updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
					if group_id.move_type != line.order_id.picking_policy:
						updated_vals.update({'move_type': line.order_id.picking_policy})
					if updated_vals:
						group_id.write(updated_vals)

			if line.product_id.kit_ids:
				values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)

				for val in values:
					if line.product_warehouse_id:
						val['warehouse_id'] = line.product_warehouse_id
					try:
						pro_id = self.env['product.product'].browse(val.get('product_id'))
						stock_id = self.env['stock.location'].browse(val.get('partner_dest_id'))
						product_uom_obj = self.env['uom.uom'].browse(val.get('product_uom'))
						procurements.append(self.env['procurement.group'].Procurement(
							pro_id, val.get('product_qty'), product_uom_obj,
							line.order_id.partner_shipping_id.property_stock_customer,
							val.get('name'), val.get('origin'), line.order_id.company_id, val
						))
					except UserError as error:
						errors.append(error.name)
			else:
				values = line._prepare_procurement_values(group_id=group_id)

				if line.product_warehouse_id:
					values['warehouse_id'] = line.product_warehouse_id

				product_qty = line.product_uom_qty - qty

				line_uom = line.product_uom
				quant_uom = line.product_id.uom_id
				product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
				procurements.append(self.env['procurement.group'].Procurement(
					line.product_id, product_qty, procurement_uom,
					line.order_id.partner_shipping_id.property_stock_customer,
					line.name, line.order_id.name, line.order_id.company_id, values))
		if procurements:
			self.env['procurement.group'].run(procurements)
		
		module = self.env['ir.module.module'].sudo().search([('state', '=', 'installed'),('name', '=', 'procurement_jit')],limit=1)
		
		if module:
			orders = list(set(x.order_id for x in self))
			for order in orders:
				reassign = order.picking_ids.filtered(lambda x: x.state=='confirmed' or (x.state in ['waiting', 'assigned'] and not x.printed))
				if reassign:
					reassign.action_assign()

		# This next block is currently needed only because the scheduler trigger is done by picking confirmation rather than stock.move confirmation
		orders = self.mapped('order_id')
		for order in orders:
			pickings_to_confirm = order.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done'])
			if pickings_to_confirm:
				# Trigger the Scheduler for Pickings
				pickings_to_confirm.action_confirm()
		return True


	def _prepare_procurement_values(self, group_id=False):
		res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
		values = []
		date_planned = self.order_id.date_order\
			+ timedelta(days=self.customer_lead or 0.0) - timedelta(days=self.order_id.company_id.security_lead)
		if  self.product_id.kit_ids:
			for item in self.product_id.kit_ids:
				line_route_ids = self.env['stock.location'].browse(self.route_id.id)
       # line_route_ids = self.env['stock.location.route'].browse(self.route_id.id)
				line_route_ids = self.env['stock.route'].browse(self.route_id.id)
				values.append({
					'name': item.product_id.name,
					'origin': self.order_id.name,
					'date_planned': date_planned,
					'product_id': item.product_id.id,
					'product_qty': item.qty_uom * abs(self.product_uom_qty),
					'product_uom': item.uom_id and item.uom_id.id,
					'company_id': self.order_id.company_id,
					'group_id': group_id,
					'sale_line_id': self.id,
					'warehouse_id' : self.order_id.warehouse_id and self.order_id.warehouse_id,
					'location_id': self.order_id.partner_shipping_id.property_stock_customer.id,
					'route_ids': self.route_id and line_route_ids or [],
					'partner_dest_id': self.order_id.partner_shipping_id,
					'partner_id': self.order_id.partner_shipping_id.id,
					'pack_id' : item.id,
				})
			return values
		else:
			res.update({
				'company_id': self.order_id.company_id,
				'group_id': group_id,
				'sale_line_id': self.id,
				'date_planned': date_planned,
				'route_ids': self.route_id,
				'warehouse_id': self.order_id.warehouse_id or False,
				'partner_dest_id': self.order_id.partner_shipping_id,
				'partner_id': self.order_id.partner_shipping_id.id,
				'company_id': self.order_id.company_id,
			})    
		return res
		

class ProcurementRule(models.Model):
	_inherit = 'stock.rule'

	@api.model
	def _run_pull(self, procurements):
		moves_values_by_company = defaultdict(list)
		mtso_products_by_locations = defaultdict(list)

		# To handle the `mts_else_mto` procure method, we do a preliminary loop to
		# isolate the products we would need to read the forecasted quantity,
		# in order to to batch the read. We also make a sanitary check on the
		# `location_src_id` field.
		for procurement, rule in procurements:
			if not rule.location_src_id:
				msg = _('No source location defined on stock rule: %s!') % (rule.name, )
				raise ProcurementException([(procurement, msg)])

			if rule.procure_method == 'mts_else_mto':
				mtso_products_by_locations[rule.location_src_id].append(procurement.product_id.id)

		# Get the forecasted quantity for the `mts_else_mto` procurement.
		forecasted_qties_by_loc = {}
		for location, product_ids in mtso_products_by_locations.items():
			products = self.env['product.product'].browse(product_ids).with_context(location=location.id)
			forecasted_qties_by_loc[location] = {product.id: product.free_qty for product in products}

		# Prepare the move values, adapt the `procure_method` if needed.
		procurements = sorted(procurements, key=lambda proc: float_compare(proc[0].product_qty, 0.0, precision_rounding=proc[0].product_uom.rounding) > 0)
		for procurement, rule in procurements:
			procure_method = rule.procure_method
			if rule.procure_method == 'mts_else_mto':
				qty_needed = procurement.product_uom._compute_quantity(procurement.product_qty, procurement.product_id.uom_id)
				if float_compare(qty_needed, 0, precision_rounding=procurement.product_id.uom_id.rounding) <= 0:
					forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_needed
					procure_method = 'make_to_order'
				elif float_compare(qty_needed, forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id],
									precision_rounding=procurement.product_id.uom_id.rounding) > 0:
					procure_method = 'make_to_order'
				else:
					forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_needed
					procure_method = 'make_to_stock'

			move_values = rule._get_stock_move_values(*procurement)
			if procurement[-1].get('pack_id'):
				move_values.update({'pack_id':procurement[-1].get('pack_id')})
			move_values['procure_method'] = procure_method
			moves_values_by_company[procurement.company_id.id].append(move_values)

		for company_id, moves_values in moves_values_by_company.items():
			# create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
			moves = self.env['stock.move'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(moves_values)
			# Since action_confirm launch following procurement_group we should activate it.
			moves._action_confirm()
		return True
	

	def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
		result = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
		
		if  product_id.kit_ids:
			for item in product_id.kit_ids:
				result.update({
					'product_id': item.product_id.id,
					'product_uom': item.uom_id and item.uom_id.id,
					'product_uom_qty': item.qty_uom,
					'origin': origin,
					'pack_id': item.id,
					})
		return result
