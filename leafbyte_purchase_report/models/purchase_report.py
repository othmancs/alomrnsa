from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseReport(models.Model):
    _name = 'purchase.report'
    _description = 'Purchase Report'

    name = fields.Char('Name')

    # Main Fields
    company_id = fields.Many2one('res.company')
    date_order = fields.Datetime('Datetime')
    partner_id = fields.Many2one('res.partner')
    product_id = fields.Many2one('product.product')
    qty = fields.Float()
    uom_id = fields.Many2one('uom.uom')
    price_unit = fields.Float()
    price_tax = fields.Float()
    tax_id = fields.Many2many('account.tax')
    subtotal = fields.Float()
    total = fields.Float()

    purchase_order_id = fields.Many2one('purchase.order')

    def get_view(self, view_id=None, view_type='tree', **options):
        res = super(PurchaseReport, self).get_view(view_id, view_type, **options)
        self.fetch_purchase_data()
        return res

    def fetch_purchase_data(self):
        # cleaning data
        purchase_report = self.env['purchase.report'].search([]).unlink()

        # purchase order
        purchase_order_line = self.env['purchase.order.line'].search([('state','=','purchase')])
        if purchase_order_line:
            for line in purchase_order_line:
                purchases_report = self.env['purchase.report'].create({
                    'company_id': line.company_id.id,
                    'name': line.order_id.name,
                    'date_order': line.order_id.date_order,
                    'partner_id': line.order_id.partner_id.id,
                    'product_id': line.product_id.id,
                    'qty': line.product_qty,
                    'uom_id': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'price_tax': line.price_tax,
                    'tax_id': line.taxes_id.ids,
                    'subtotal': line.price_subtotal,
                    'total': line.price_total,
                    'purchase_order_id' : line.order_id.id
                })