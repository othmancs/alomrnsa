# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo import tools


class WarrantyReport(models.Model):
    """ Warranty Report """
    _name="warranty.report"
    _auto=False
    _description="Warranty Report"

    warranty_no = fields.Char(string="Number")
    template_id = fields.Many2one('warranty.template', string="Template")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    partner_id = fields.Many2one('res.partner', string="Customer")
    user_id = fields.Many2one('res.users', string="Salesperson")
    product_id = fields.Many2one('product.product', string="Product")
    serial_id = fields.Many2one('stock.lot', string="Serial")
    sale_id = fields.Many2one('sale.order', string="Order")
    sale_line_id = fields.Many2one('sale.order.line', string="Order Line")
    sale_invoice_id = fields.Many2one('account.move', string="Sale Invoice")
    invoice_id = fields.Many2one('account.move', string="Invoice")
    company_id = fields.Many2one('res.company', string="Company")
    state = fields.Selection([('draft', 'Draft'),
                                ('pending', 'Pending'),
                                ('confirm', 'Confirmed'),
                                ('running', 'Running'),
                                ('expired', 'Expired'),
                                ('cancel', 'Cancelled')], string="Status")
    confirm_by = fields.Many2one('res.users', string="Confirmed By")
    confirm_date = fields.Datetime(string="Confirmed Date")
    cancel_by = fields.Many2one('res.users', string="Cancelled By")
    cancel_date = fields.Datetime(string="Cancelled Date")
    # parent_id = fields.Many2one('warranty.detail', string="Parent")
    warranty_renew_cost = fields.Float(string="Renew Cost")

    # @api.model
    def _select(self):
        select_str = """
            SELECT
                    min(w.id) as id,
                    w.warranty_no,
                    w.template_id,
                    w.start_date,
                    w.end_date,
                    w.partner_id,
                    w.user_id,
                    w.product_id,
                    w.serial_id,
                    w.sale_id,
                    w.sale_line_id,
                    w.sale_invoice_id,
                    w.invoice_id,
                    w.company_id,
                    w.state,
                    w.confirm_by,
                    w.confirm_date,
                    w.cancel_by,
                    w.cancel_date,
                    -- w.parent_id,
                    w.warranty_renew_cost
        """
        return select_str

    # @api.model
    def _from(self):
        from_str = """
            FROM
                warranty_detail w
        """
        return from_str

    # @api.model
    def _group_by(self):
        group_by_str = """
                GROUP BY  w.warranty_no,w.template_id,w.start_date,w.end_date,
                    w.partner_id,w.user_id,w.product_id,w.serial_id,w.sale_id,w.sale_line_id,
                    w.sale_invoice_id,w.invoice_id,w.company_id,w.state,w.confirm_by,w.confirm_date,
                    w.cancel_by,w.cancel_date,w.warranty_renew_cost
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s as (
                %s %s %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
