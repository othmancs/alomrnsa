# -- coding: utf-8 --
#################################################################################
# Author      : Plus Technology Co.Ltd. (<https://www.plustech-it.com//>)
# Copyright(c): 2024-Plus Technology Co. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
from odoo import fields, models, _, api
from collections import defaultdict
from datetime import date, datetime, timedelta
import pytz


class SalesProductsWizard(models.TransientModel):
    _name = "sale.products.wizard"
    _description = "Sale Products Report"

    date_from = fields.Date(string='Date')
    date_to = fields.Date(string='Date')
    product_ids = fields.Many2many('product.product')
    product_category_ids = fields.Many2many('product.category')
    include_pos = fields.Boolean('Include Point Of Sale ?')

    @api.onchange('product_category_ids')
    def _get_product_ids(self):
        self.product_ids = self.env['product.product'].search(
            [('categ_id', 'in', self.product_category_ids.ids)])

    def _query(self):
        if self.include_pos:
            query = """
                WITH merged_data AS (
        SELECT
            p.id AS product_id,
            tmpl.name AS name,
            MAX(tmpl.list_price) AS list_price,
            SUM(CASE WHEN am.move_type = 'out_invoice' THEN aml.quantity ELSE 0 END) AS total_quantity,
            SUM(CASE WHEN am.move_type = 'out_invoice' THEN (aml.discount * aml.price_subtotal) / 100 ELSE 0 END) AS total_discount_amount,  
            SUM(CASE WHEN am.move_type = 'out_invoice' THEN aml.price_subtotal + (aml.discount * aml.price_subtotal) / 100 ELSE 0 END) AS total_price_subtotal,
            SUM(CASE WHEN am.move_type = 'out_invoice' THEN aml.price_total ELSE 0 END) AS total_price_total,
            SUM(CASE WHEN am.move_type = 'out_invoice' THEN aml.price_total - aml.price_subtotal ELSE 0 END) AS total_tax_amount,
            SUM(CASE WHEN am.move_type = 'out_refund' THEN aml.price_total ELSE 0 END) AS refund_total_price_total,
            SUM(CASE WHEN am.move_type = 'out_refund' THEN aml.quantity ELSE 0 END) AS refund_quantity
        FROM  account_move_line aml
        JOIN account_move am ON aml.move_id = am.id
        JOIN product_product p ON aml.product_id = p.id
        LEFT JOIN product_template tmpl ON p.product_tmpl_id = tmpl.id
        WHERE
            am.state = 'posted'
            AND am.move_type IN ('out_invoice', 'out_refund')
            AND aml.product_id IS NOT NULL
            AND am.company_id = %s
            AND (%s IS NULL OR (am.date >= %s AND am.date <= %s))
            AND (NOT %s OR aml.product_id = ANY(%s))
        GROUP BY
            aml.product_id, p.id, tmpl.name

        UNION
    
        SELECT
            p.id AS product_id,
            tmpl.name AS name,
            MAX(tmpl.list_price) AS list_price,
            SUM(CASE WHEN pos.state not in ('draft', 'cancel') AND pol.qty > 0 THEN pol.qty ELSE 0 END) AS total_quantity,
            SUM(CASE WHEN pos.state not in ('draft', 'cancel') AND pol.qty > 0 THEN (pol.discount * pol.price_subtotal_incl) / 100 ELSE 0 END) AS total_discount_amount,
            SUM(CASE WHEN pos.state not in ('draft', 'cancel') AND pol.qty > 0 THEN pol.price_subtotal_incl + (pol.discount * pol.price_subtotal_incl) / 100 ELSE 0 END) AS total_price_subtotal,
            SUM(CASE WHEN pos.state not in ('draft', 'cancel') AND pol.qty > 0 THEN pol.price_subtotal_incl ELSE 0 END) AS total_price_total,
            SUM(CASE WHEN pos.state not in ('draft', 'cancel') AND pol.qty > 0 THEN pol.price_subtotal_incl - pol.price_subtotal ELSE 0 END) AS total_tax_amount,
            SUM(CASE WHEN pos.state not in ('draft', 'cancel') AND pol.qty < 0 THEN -pol.price_subtotal_incl ELSE 0 END) AS refund_total_price_total,
            SUM(CASE WHEN pos.state not in ('draft', 'cancel') AND pol.qty < 0 THEN -pol.qty ELSE 0 END) AS refund_quantity
        FROM pos_order_line pol
        JOIN pos_order pos ON pol.order_id = pos.id
        JOIN product_product p ON pol.product_id = p.id
        LEFT JOIN product_template tmpl ON p.product_tmpl_id = tmpl.id
        WHERE
            pos.state not in ('draft', 'cancel')
            AND pos.company_id = %s
            AND pol.product_id IS NOT NULL
            AND (%s IS NULL OR (pos.date_order >= %s AND pos.date_order <= %s))
            AND (NOT %s OR pol.product_id = ANY(%s))        
        GROUP BY
            pol.product_id, p.id, tmpl.name
    )
    SELECT
        product_id,
        name,
        MAX(list_price) AS list_price,
        SUM(total_quantity) AS total_quantity,
        SUM(total_discount_amount) AS total_discount_amount,
        SUM(total_price_subtotal) AS total_price_subtotal,
        SUM(total_price_total) AS total_price_total,
        SUM(total_tax_amount) AS total_tax_amount,
        SUM(refund_total_price_total) AS refund_total_price_total,
        SUM(refund_quantity) AS refund_quantity
    FROM
        merged_data
    GROUP BY
        product_id, name ;
        """
        else:
            query = """
                SELECT
                    p.id AS product_id,
                    tmpl.name AS name,
                    MAX(tmpl.list_price) AS list_price,
                    SUM(CASE WHEN am.move_type = 'out_invoice' THEN aml.quantity ELSE 0 END) AS total_quantity,
                    SUM(CASE WHEN am.move_type = 'out_invoice' THEN (aml.discount * aml.price_subtotal) / 100 ELSE 0 END) AS total_discount_amount,  
                    SUM(CASE WHEN am.move_type = 'out_invoice' THEN aml.price_subtotal + (aml.discount * aml.price_subtotal) / 100 ELSE 0 END) AS total_price_subtotal,
                    SUM(CASE WHEN am.move_type = 'out_invoice' THEN aml.price_total ELSE 0 END) AS total_price_total,
                    SUM(CASE WHEN am.move_type = 'out_invoice' THEN aml.price_total - aml.price_subtotal ELSE 0 END) AS total_tax_amount,
                    SUM(CASE WHEN am.move_type = 'out_refund' THEN aml.price_total ELSE 0 END) AS refund_total_price_total,
                    SUM(CASE WHEN am.move_type = 'out_refund' THEN aml.quantity ELSE 0 END) AS refund_quantity
                FROM  account_move_line aml
                JOIN account_move am ON aml.move_id = am.id
                JOIN product_product p ON aml.product_id = p.id
                LEFT JOIN product_template tmpl ON p.product_tmpl_id = tmpl.id
                WHERE
                    am.state = 'posted'
                    AND am.move_type IN ('out_invoice', 'out_refund')
                    AND aml.product_id IS NOT NULL
                    AND am.company_id = %s
                    AND (%s IS NULL OR (am.date >= %s AND am.date <= %s))
                    AND (NOT %s OR aml.product_id = ANY(%s))
                GROUP BY
                    aml.product_id, p.id, tmpl.name
                """

        company = self.env.company.id
        user_timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        date_from = self.date_from if self.date_from else None
        date_to = self.date_to if self.date_to else None
        if date_from and date_to:
            date_with_time = datetime.combine(self.date_from, datetime.min.time())
            localized_datetime = user_timezone.localize(date_with_time)
            utc_datetime = localized_datetime.astimezone(pytz.UTC)
            date_from_pos = utc_datetime

            date_with_time2 = datetime.combine(self.date_to, datetime.max.time())
            localized_datetime2 = user_timezone.localize(date_with_time2)
            utc_datetime2 = localized_datetime2.astimezone(pytz.UTC)
            date_to_pos = utc_datetime2
        else:
            date_from_pos = None
            date_to_pos = None

        product_ids = self.product_ids.ids if self.product_ids.ids else []
        include_product_condition = bool(product_ids)
        if self.include_pos:
            self._cr.execute(query, [company, date_to, date_from, date_to, include_product_condition, product_ids,
                                     company, date_to_pos, date_from_pos, date_to_pos, include_product_condition,
                                     product_ids])
        else:
            self._cr.execute(query,
                             [company, date_to, date_from, date_to, include_product_condition, product_ids,
                              ])
        products = self.env.cr.dictfetchall()
        return products

    def print_xlsx(self):
        data = {
            'form_data': self.read()[0]
        }
        return self.env.ref('plustech_product_sales_report.report_product_sales_xlsx').report_action(self)

    def print_pdf(self):
        products = self._query()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'data': products,
        }
        return self.env.ref('plustech_product_sales_report.report_product_sales_pdf').with_context(landscape=True).report_action(
            self, data=data)

    def open_view(self):
        self.env['sale.products.report'].sudo().search([]).unlink()
        products = self._query()
        print(products)
        vals_list = []
        for product in products:
            vals = {
                'product_id': product['product_id'],
                'total_price_subtotal': product['total_price_subtotal'],
                'total_discount_amount': product['total_discount_amount'],
                'total_price_total': product['total_price_total'],
                'total_tax_amount': product['total_tax_amount'],
                'total_quantity': product['total_quantity'],
                'list_price': product['list_price'],
                'refund_total_price_total': product['refund_total_price_total'],
                'refund_quantity': product['refund_quantity'],
            }
            vals_list.append(vals)

        self.env['sale.products.report'].create(vals_list)
        return {
            'view_mode': 'tree,graph',
            'name': (_('Product Sales & Refunds')),
            'res_model': 'sale.products.report',
            'type': 'ir.actions.act_window',
        }
