# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools,_
import json
from odoo.exceptions import RedirectWarning, UserError, ValidationError ,Warning
from odoo.tools import float_is_zero, float_compare,format_datetime
from itertools import groupby
from collections import defaultdict


class Product(models.Model):
	_inherit = 'product.product'


	def _product_domain(self, product_template_ids, product_variant_ids):
		if product_template_ids:
			return [('product_tmpl_id', 'in', product_template_ids)]
		return [('product_id', 'in', product_variant_ids)]

	def _move_domain(self, product_template_ids, product_variant_ids, wh_location_ids):
		move_domain = self._product_domain(product_template_ids, product_variant_ids)
		move_domain += [('product_uom_qty', '!=', 0)]
		out_domain = move_domain + [
			'&',
			('location_id', 'in', wh_location_ids),
			('location_dest_id', 'not in', wh_location_ids),
		]
		in_domain = move_domain + [
			'&',
			('location_id', 'not in', wh_location_ids),
			('location_dest_id', 'in', wh_location_ids),
		]
		return in_domain, out_domain

	def _move_draft_domain(self, product_template_ids, product_variant_ids, wh_location_ids):
		in_domain, out_domain = self._move_domain(product_template_ids, product_variant_ids, wh_location_ids)
		in_domain += [('state', '=', 'draft')]
		out_domain += [('state', '=', 'draft')]
		return in_domain, out_domain

	def _move_confirmed_domain(self, product_template_ids, product_variant_ids, wh_location_ids):
		in_domain, out_domain = self._move_domain(product_template_ids, product_variant_ids, wh_location_ids)
		out_domain += [('state', 'not in', ['draft', 'cancel', 'done'])]
		in_domain += [('state', 'not in', ['draft', 'cancel', 'done'])]
		return in_domain, out_domain

	def _compute_draft_quantity_count(self, product_template_ids, product_variant_ids, wh_location_ids):
		in_domain, out_domain = self._move_draft_domain(product_template_ids, product_variant_ids, wh_location_ids)
		incoming_moves = self.env['stock.move'].read_group(in_domain, ['product_qty:sum'], 'product_id')
		outgoing_moves = self.env['stock.move'].read_group(out_domain, ['product_qty:sum'], 'product_id')
		in_sum = sum(move['product_qty'] for move in incoming_moves)
		out_sum = sum(move['product_qty'] for move in outgoing_moves)
		return {
			'draft_picking_qty': {
				'in': in_sum,
				'out': out_sum
			},
			'qty': {
				'in': in_sum,
				'out': out_sum
			}
		}

	@api.model
	def _get_report_values(self, docids, data=None):
		return {
			'data': data,
			'doc_ids': docids,
			'doc_model': 'product.product',
			'docs': self._get_report_data(product_variant_ids=docids),
		}

	def _get_report_data(self, product_template_ids=False, product_variant_ids=False):
		assert product_template_ids or product_variant_ids
		res = {}

		# Get the warehouse we're working on as well as its locations.
		if self.env.context.get('warehouse'):
			warehouse = self.env['stock.warehouse'].sudo().browse(self.env.context['warehouse'])
		else:
			warehouse = self.env['stock.warehouse'].sudo().search([
				('company_id', '=', self.env.company.id)
			], limit=1)
			self.env.context = dict(self.env.context, warehouse=warehouse.id)
		wh_location_ids = [loc['id'] for loc in self.env['stock.location'].search_read(
			[('id', 'child_of', warehouse.view_location_id.id)],
			['id'],
		)]
		res['active_warehouse'] = warehouse.display_name

		# Get the products we're working, fill the rendering context with some of their attributes.
	   
		if product_template_ids:
			product_templates = self.env['product.template'].browse(product_template_ids)
			res['product_templates'] = product_templates
			res['product_variants'] = product_templates.product_variant_ids
			res['multiple_product'] = len(product_templates.product_variant_ids) > 1
			res['uom'] = product_templates[:1].uom_id.display_name
			res['quantity_on_hand'] = sum(product_templates.mapped('qty_available'))
			res['virtual_available'] = sum(product_templates.mapped('virtual_available'))
		
		if product_variant_ids:
			product_variants = self.env['product.product'].browse(product_variant_ids)
			res['product_templates'] = False
			res['product_variants'] = product_variants
			res['multiple_product'] = len(product_variants) > 1
			res['uom'] = product_variants[:1].uom_id.display_name
			res['quantity_on_hand'] = sum(product_variants.mapped('qty_available'))
			res['virtual_available'] = sum(product_variants.mapped('virtual_available'))
		res.update(self._compute_draft_quantity_count(product_template_ids, product_variant_ids, wh_location_ids))

		res['lines'] = self._get_report_lines(product_template_ids, product_variant_ids, wh_location_ids)
		return res

	def _prepare_report_line(self, quantity, move_out=None, move_in=None, replenishment_filled=True, product=False, reservation=False):
		timezone = self._context.get('tz')
		product = product or (move_out.product_id if move_out else move_in.product_id)
		is_late = move_out.date < move_in.date if (move_out and move_in) else False
		return {
			'document_in': move_in._get_source_document() if move_in else False,
			'document_out': move_out._get_source_document() if move_out else False,
			'product': {
				'id': product.id,
				'display_name': product.display_name
			},
			'replenishment_filled': replenishment_filled,
			'uom_id': product.uom_id,
			'receipt_date': format_datetime(self.env, move_in.date, timezone, 'medium') if move_in else False,
			'delivery_date': format_datetime(self.env, move_out.date, timezone, 'medium') if move_out else False,
			'is_late': is_late,
			'quantity': quantity,
			'move_out': move_out,
			'move_in': move_in,
			'reservation': reservation,
		}

	def _get_report_lines(self, product_template_ids, product_variant_ids, wh_location_ids):
		in_domain, out_domain = self._move_confirmed_domain(
			product_template_ids, product_variant_ids, wh_location_ids
		)
		outs = self.env['stock.move'].search(out_domain, order='priority desc, date, id')
		outs_per_product = defaultdict(lambda: [])
		for out in outs:
			outs_per_product[out.product_id.id].append(out)
		ins = self.env['stock.move'].search(in_domain, order='priority desc, date, id')
		ins_per_product = defaultdict(lambda: [])
		for in_ in ins:
			ins_per_product[in_.product_id.id].append([in_.product_qty, in_])
		currents = {c['id']: c['qty_available'] for c in outs.product_id.with_context(location=wh_location_ids).read(['qty_available'])}

		lines = []
		for product in (ins | outs).product_id:
			for out in outs_per_product[product.id]:
				if out.state not in ('partially_available', 'assigned'):
					continue
				current = currents[out.product_id.id]
				reserved = out.product_uom._compute_quantity(out.reserved_availability, product.uom_id)
				currents[product.id] -= reserved
				lines.append(self._prepare_report_line(reserved, move_out=out, reservation=True))

			for out in outs_per_product[product.id]:
				# Reconcile with the current stock.
				current = currents[out.product_id.id]
				reserved = 0.0
				if out.state in ('partially_available', 'assigned'):
					reserved = out.product_uom._compute_quantity(out.reserved_availability, product.uom_id)
				demand = out.product_qty - reserved
				taken_from_stock = min(demand, current)
				if not float_is_zero(taken_from_stock, precision_rounding=product.uom_id.rounding):
					currents[product.id] -= taken_from_stock
					demand -= taken_from_stock
					lines.append(self._prepare_report_line(taken_from_stock, move_out=out))
				# Reconcile with the ins.
				if not float_is_zero(demand, precision_rounding=product.uom_id.rounding):
					index_to_remove = []
					for index, in_ in enumerate(ins_per_product[out.product_id.id]):
						if float_is_zero(in_[0], precision_rounding=product.uom_id.rounding):
							continue
						taken_from_in = min(demand, in_[0])
						demand -= taken_from_in
						lines.append(self._prepare_report_line(taken_from_in, move_in=in_[1], move_out=out))
						ins_per_product[out.product_id.id][index][0] -= taken_from_in
						if ins_per_product[out.product_id.id][index][0] <= 0:
							index_to_remove.append(index)
						if float_is_zero(demand, precision_rounding=product.uom_id.rounding):
							break
					for index in index_to_remove[::-1]:
						ins_per_product[out.product_id.id].pop(index)
				# Not reconciled.
				if not float_is_zero(demand, precision_rounding=product.uom_id.rounding):
					lines.append(self._prepare_report_line(demand, move_out=out, replenishment_filled=False))
			# Unused remaining stock.
			free_stock = currents.get(product.id, 0)
			if not float_is_zero(free_stock, precision_rounding=product.uom_id.rounding):
				lines.append(self._prepare_report_line(free_stock, product=product))
			# In moves not used.
			for in_ in ins_per_product[product.id]:
				if float_is_zero(in_[0], precision_rounding=product.uom_id.rounding):
					continue
				lines.append(self._prepare_report_line(in_[0], move_in=in_[1]))
		return lines

	@api.model
	def get_filter_state(self):
		res = {}
		res['warehouses'] = self.env['stock.warehouse'].search_read(fields=['id', 'name', 'code'])
		res['active_warehouse'] = self.env.context.get('warehouse', False)
		if not res['active_warehouse']:
			res['active_warehouse'] = self.env.context.get('allowed_company_ids')[0]
		return res
