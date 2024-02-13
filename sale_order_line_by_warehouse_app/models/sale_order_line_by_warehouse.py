# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang, get_lang
from odoo.exceptions import UserError


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	@api.onchange('warehouse_id')
	def onchange_warehouses_id(self):
		for order in self:
			if order.warehouse_id:
				for line in order.order_line:
					line.warehouses_id = order.warehouse_id.id

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	warehouses_id = fields.Many2one('stock.warehouse',string="Warehouse")
	is_warehouse = fields.Boolean(default=lambda self: self.env.company.allow_warehouse)

	@api.onchange('product_id', 'order_id', 'order_id.warehouse_id')
	def set_required_warehouse(self):
		if self.product_id:
			allow_warehouse = self.env.company.allow_warehouse
			self.is_warehouse = allow_warehouse
		if self.order_id.warehouse_id:
			self.warehouses_id = self.order_id.warehouse_id.id

	def _action_launch_stock_rule(self, previous_product_uom_qty=False):
		"""
		Launch procurement group run method with required/custom fields genrated by a
		sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
		depending on the sale order line product rule.
		"""
		allow_warehouse = self.env.company.allow_warehouse
		if not allow_warehouse:
			res = super(SaleOrderLine, self)._action_launch_stock_rule()
			return res

		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
		procurements = []
		for line in self:
			if line.state != 'sale' or not line.product_id.type in ('consu','product'):
				continue
			qty = line._get_qty_procurement(previous_product_uom_qty)
			if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
				continue
			group_id = line._get_procurement_group()
			if not group_id:
				group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
				line.order_id.procurement_group_id = group_id
			else:
				# In case the procurement group is already created and the order was
				# cancelled, we need to update certain values of the group.
				updated_vals = {}
				if group_id.partner_id != line.order_id.partner_shipping_id:
					updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
				if group_id.move_type != line.order_id.picking_policy:
					updated_vals.update({'move_type': line.order_id.picking_policy})
				if updated_vals:
					group_id.write(updated_vals)
			ware = line.warehouses_id
			values = line._prepare_procurement_values(group_id=group_id)
			if ware:
				if values.get('warehouse_id'):
					values.update({'warehouse_id': line.warehouses_id})
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
		return True

	@api.onchange('product_id', 'warehouses_id','product_uom_qty')
	def product_id_change(self):
		if not self.product_id:
			return
		valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
		# remove the is_custom values that don't belong to this template
		for pacv in self.product_custom_attribute_value_ids:
			if pacv.custom_product_template_attribute_value_id not in valid_values:
				self.product_custom_attribute_value_ids -= pacv

		# remove the no_variant attributes that don't belong to this template
		for ptav in self.product_no_variant_attribute_value_ids:
			if ptav._origin not in valid_values:
				self.product_no_variant_attribute_value_ids -= ptav

		vals = {}
		if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
			vals['product_uom'] = self.product_id.uom_id
			vals['product_uom_qty'] = self.product_uom_qty or 1.0

		product = self.product_id.with_context(
			lang=get_lang(self.env, self.order_id.partner_id.lang).code,
			partner=self.order_id.partner_id,
			quantity=vals.get('product_uom_qty') or self.product_uom_qty,
			date=self.order_id.date_order,
			pricelist=self.order_id.pricelist_id.id,
			uom=self.product_uom.id
		)

		vals.update(name=self._get_sale_order_line_multiline_description_sale())

		self._compute_tax_id()

		if self.order_id.pricelist_id and self.order_id.partner_id:
			vals['price_unit'] = self.with_company(self.company_id)._get_display_price()
		self.update(vals)
		result = {}
		if self.warehouses_id:
			res = self._compute_quantities_dict(self.product_id,
										warehouse_id = self.warehouses_id, 
										from_date = self._context.get('from_date'),
										to_date = self._context.get('to_date'))
			qty_available     = res.get(self.product_id.id).get('qty_available') or 0.0
			incoming_qty      = res.get(self.product_id.id).get('incoming_qty') or 0.0
			outgoing_qty      = res.get(self.product_id.id).get('outgoing_qty') or 0.0
			virtual_available = res.get(self.product_id.id).get('virtual_available') or 0.0
			net_on_hand_qty   = (qty_available - outgoing_qty) or 0.0
			if qty_available <= 0.0 or self.product_uom_qty > qty_available:
				message =  _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
						(self.product_uom_qty, self.product_uom.name, self.product_id.name, qty_available, product.uom_id.name, self.warehouses_id.name)
				warning_mess = {
					'title': _('Not enough inventory!'),
					'message' : message
				}
				result = {'warning': warning_mess}
		return result

	def _get_domain_locations(self, warehouse_id):
		'''
		Parses the context and returns a list of location_ids based on it.
		It will return all stock locations when no parameters are given
		Possible parameters are shop, warehouse, location, force_company, compute_child
		'''
		Warehouse = self.env['stock.warehouse']
		location_ids = []
		if warehouse_id:
			if isinstance(warehouse_id.id, list):
				wids = [warehouse_id.id]
			elif isinstance(warehouse_id.id, list):
				domain = [('name', 'ilike', warehouse_id.id)]
				if self.env.context.get('force_company', False):
					domain += [('company_id', '=', self.env.context['force_company'])]
				wids = Warehouse.search(domain).ids
			else:
				wids = warehouse_id.id
		else:
			wids = Warehouse.search([]).ids

		for w in Warehouse.browse(wids):
			location_ids.append(w.view_location_id.id)
		return self._get_domain_locations_new(location_ids, company_id=self.env.context.get('force_company', False), compute_child=self.env.context.get('compute_child', True))

	def _get_domain_locations_new(self, location_ids, company_id=False, compute_child=True):
		operator = compute_child and 'child_of' or 'in'
		domain = company_id and ['&', ('company_id', '=', company_id)] or []
		locations = self.env['stock.location'].browse(location_ids)
		# TDE FIXME: should move the support of child_of + auto_join directly in expression
		hierarchical_locations = locations if operator == 'child_of' else locations.browse()
		other_locations = locations - hierarchical_locations
		loc_domain = []
		dest_loc_domain = []
		# this optimizes [('location_id', 'child_of', hierarchical_locations.ids)]
		# by avoiding the ORM to search for children locations and injecting a
		# lot of location ids into the main query
		for location in hierarchical_locations:
			loc_domain = loc_domain and ['|'] + loc_domain or loc_domain
			loc_domain.append(('location_id.parent_path', '=like', location.parent_path + '%'))
			dest_loc_domain = dest_loc_domain and ['|'] + dest_loc_domain or dest_loc_domain
			dest_loc_domain.append(('location_dest_id.parent_path', '=like', location.parent_path + '%'))
		if other_locations:
			loc_domain = loc_domain and ['|'] + loc_domain or loc_domain
			loc_domain = loc_domain + [('location_id', operator, other_locations.ids)]
			dest_loc_domain = dest_loc_domain and ['|'] + dest_loc_domain or dest_loc_domain
			dest_loc_domain = dest_loc_domain + [('location_dest_id', operator, other_locations.ids)]
		return (
			domain + loc_domain,
			domain + dest_loc_domain + ['!'] + loc_domain if loc_domain else domain + dest_loc_domain,
			domain + loc_domain + ['!'] + dest_loc_domain if dest_loc_domain else domain + loc_domain
		)

	def _compute_quantities_dict(self, product_id, lot_id=False, owner_id=False, package_id=False, location_id=False , warehouse_id=False, from_date=False, to_date=False):
		domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations(warehouse_id)
		domain_quant = [('product_id', 'in', [product_id.id])] + domain_quant_loc
		dates_in_the_past = False
		# only to_date as to_date will correspond to qty_available
		to_date = fields.Datetime.to_datetime(to_date)
		if to_date and to_date < fields.Datetime.now():
			dates_in_the_past = True

		domain_move_in = [('product_id', 'in', [product_id.id])] + domain_move_in_loc
		domain_move_out = [('product_id', 'in', [product_id.id])] + domain_move_out_loc
		if lot_id is not None:
			domain_quant += [('lot_id', '=', lot_id)]
		if owner_id is not None:
			domain_quant += [('owner_id', '=', owner_id)]
			domain_move_in += [('restrict_partner_id', '=', owner_id)]
			domain_move_out += [('restrict_partner_id', '=', owner_id)]
		if package_id is not None:
			domain_quant += [('package_id', '=', package_id)]
		if dates_in_the_past:
			domain_move_in_done = list(domain_move_in)
			domain_move_out_done = list(domain_move_out)
		if from_date:
			domain_move_in += [('date', '>=', from_date)]
			domain_move_out += [('date', '>=', from_date)]
		if to_date:
			domain_move_in += [('date', '<=', to_date)]
			domain_move_out += [('date', '<=', to_date)]

		Move = self.env['stock.move']
		Quant = self.env['stock.quant']
		domain_move_in_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
		domain_move_out_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
		moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
		moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
		quants_res = dict((item['product_id'][0], item['quantity']) for item in Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))
		if dates_in_the_past:
			# Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
			domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
			domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
			moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
			moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
		res = dict()
		for product in [product_id.id]:
			product_id = product
			product = self.env['product.product'].browse(product_id)
			rounding = product.uom_id.rounding
			res[product_id] = {}
			if dates_in_the_past:
				qty_available = quants_res.get(product_id, 0.0) - moves_in_res_past.get(product_id, 0.0) + moves_out_res_past.get(product_id, 0.0)
			else:
				qty_available = quants_res.get(product_id, 0.0)
			res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
			res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0), precision_rounding=rounding)
			res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0), precision_rounding=rounding)
			res[product_id]['virtual_available'] = float_round(
				qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
				precision_rounding=rounding)
		return res
