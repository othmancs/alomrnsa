# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class SaleReport(models.Model):
    _inherit = 'sale.report'

    product_kit = fields.Many2one('product.product', 'Product Kit', readonly=True)

    def _select_additional_fields(self):
        res = super(SaleReport, self)._select_additional_fields()
        res['product_kit'] = "l.product_id as product_kit"
        return res

    def _group_by_sale(self):
        group_by = super(SaleReport, self)._group_by_sale()
        if 'l.product_id' not in group_by:
            group_by += ', l.product_id'
        return group_by

    @api.model
    def _query(self):
        with_ = """
            WITH currency_table AS (
                SELECT r.id, r.currency_rate
                FROM res_currency_rate r
                JOIN (
                    SELECT currency_id, MAX(name) AS name
                    FROM res_currency_rate
                    GROUP BY currency_id
                ) curr ON curr.currency_id = r.currency_id AND curr.name = r.name
            )
        """
        return f"""
            {with_}
            SELECT
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
                    / CASE WHEN COALESCE(s.currency_rate, 0) = 0 THEN 1 ELSE s.currency_rate END
                    * CASE WHEN COALESCE(currency_table.rate, 0) = 0 THEN 1 ELSE currency_table.rate END
                    ) ELSE 0
                END AS price_total,
                CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_subtotal
                    * CASE WHEN COALESCE(s.currency_rate, 0) = 0 THEN 1 ELSE s.currency_rate END
                    * CASE WHEN COALESCE(currency_table.rate, 0) = 0 THEN 1 ELSE currency_table.rate END
                    ) ELSE 0
                END AS price_subtotal,
                CASE WHEN l.product_id IS NOT NULL THEN SUM(l.untaxed_amount_to_invoice
                    * CASE WHEN COALESCE(s.currency_rate, 0) = 0 THEN 1 ELSE s.currency_rate END
                    * CASE WHEN COALESCE(currency_table.rate, 0) = 0 THEN 1 ELSE currency_table.rate END
                    ) ELSE 0
                END AS untaxed_amount_to_invoice,
                CASE WHEN l.product_id IS NOT NULL THEN SUM(l.untaxed_amount_invoiced
                    * CASE WHEN COALESCE(s.currency_rate, 0) = 0 THEN 1 ELSE s.currency_rate END
                    * CASE WHEN COALESCE(currency_table.rate, 0) = 0 THEN 1 ELSE currency_table.rate END
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
                    * CASE WHEN COALESCE(s.currency_rate, 0) = 0 THEN 1 ELSE s.currency_rate END
                    * CASE WHEN COALESCE(currency_table.rate, 0) = 0 THEN 1 ELSE currency_table.rate END
                    ) ELSE 0
                END AS discount_amount,
                s.id AS order_id
            FROM sale_order_line l
                JOIN sale_order s ON s.id = l.order_id
                JOIN res_partner partner ON s.partner_id = partner.id
                LEFT JOIN product_product p ON l.product_id = p.id
                LEFT JOIN product_template t ON p.product_tmpl_id = t.id
                LEFT JOIN uom_uom u ON u.id = l.product_uom
                LEFT JOIN uom_uom u2 ON u2.id = t.uom_id
                LEFT JOIN currency_table ON currency_table.id = s.currency_id
            WHERE l.display_type IS NULL
            GROUP BY
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
                currency_table.rate
        """
