# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _




class SaleReport(models.Model):
	_inherit = 'sale.report'



	product_kit = fields.Many2one('product.product', 'product kit', readonly=True, store=True)

 # def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
 # 	fields['product_kit'] = ", l.product_id as product_kit"
 # 	groupby += ', l.product_id'
 # 	return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
 
	def _select_sale(self):
		select_ = f"""
			COALESCE(min(l.id), -s.id) AS id,
			l.product_id AS product_id,
			l.product_id AS product_kit,
			t.uom_id AS product_uom,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.product_uom_qty / u.factor * u2.factor) ELSE 0 END AS product_uom_qty,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_delivered / u.factor * u2.factor) ELSE 0 END AS qty_delivered,
			CASE WHEN l.product_id IS NOT NULL THEN SUM((l.product_uom_qty - l.qty_delivered) / u.factor * u2.factor) ELSE 0 END AS qty_to_deliver,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_invoiced / u.factor * u2.factor) ELSE 0 END AS qty_invoiced,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_to_invoice / u.factor * u2.factor) ELSE 0 END AS qty_to_invoice,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_total
				* {self._case_value_or_one('s.currency_rate')}
				* {self._case_value_or_one('currency_table.rate')}
				) ELSE 0
			END AS price_total,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_subtotal
				* {self._case_value_or_one('s.currency_rate')}
				* {self._case_value_or_one('currency_table.rate')}
				) ELSE 0
			END AS price_subtotal,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.untaxed_amount_to_invoice
				* {self._case_value_or_one('s.currency_rate')}
				* {self._case_value_or_one('currency_table.rate')}
				) ELSE 0
			END AS untaxed_amount_to_invoice,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.untaxed_amount_invoiced
				* {self._case_value_or_one('s.currency_rate')}
				* {self._case_value_or_one('currency_table.rate')}
				) ELSE 0
			END AS untaxed_amount_invoiced,
			COUNT(*) AS nbr,
			s.name AS name,
			s.date_order AS date,
			s.state AS state,
			s.partner_id AS partner_id,
			s.user_id AS user_id,
			s.company_id AS company_id,
			s.campaign_id AS campaign_id,
			s.medium_id AS medium_id,
			s.source_id AS source_id,
			t.categ_id AS categ_id,
			s.pricelist_id AS pricelist_id,
			s.analytic_account_id AS analytic_account_id,
			s.team_id AS team_id,
			p.product_tmpl_id,
			partner.country_id AS country_id,
			partner.industry_id AS industry_id,
			partner.commercial_partner_id AS commercial_partner_id,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(p.weight * l.product_uom_qty / u.factor * u2.factor) ELSE 0 END AS weight,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(p.volume * l.product_uom_qty / u.factor * u2.factor) ELSE 0 END AS volume,
			l.discount AS discount,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_unit * l.product_uom_qty * l.discount / 100.0
				* {self._case_value_or_one('s.currency_rate')}
				* {self._case_value_or_one('currency_table.rate')}
				) ELSE 0
			END AS discount_amount,
			s.id AS order_id"""
		
		additional_fields_info = self._select_additional_fields()
		template = """,
			%s AS %s"""
		for fname, query_info in additional_fields_info.items():
			select_ += template % (query_info, fname)
		
		return select_
	
	def _group_by_sale(self):
		return """
			l.product_id,
			l.order_id,
			t.uom_id,
			t.categ_id,
			s.name,
			s.date_order,
			s.partner_id,
			s.user_id,
			s.state,
			s.company_id,
			s.campaign_id,
			s.medium_id,
			s.source_id,
			s.pricelist_id,
			s.analytic_account_id,
			s.team_id,
			p.product_tmpl_id,
			partner.country_id,
			partner.industry_id,
			partner.commercial_partner_id,
			l.discount,
			s.id,
			currency_table.rate"""
	
	def _query(self):
		with_ = self._with_sale()
		return f"""
			{"WITH" + with_ + "(" if with_ else ""}
			SELECT {self._select_sale()}
			FROM {self._from_sale()}
			WHERE {self._where_sale()}
			GROUP BY {self._group_by_sale()}
			{")" if with_ else ""}
		"""