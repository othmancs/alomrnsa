# from odoo import fields, models


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

#     payment_method = fields.Selection([
#         ('option1', 'نقدى'),
#         ('option2', 'اجل'),
#     ], string='طريقه الدفع', required=True)

#     def _prepare_invoice(self):
#         invoice_vals = super(SaleOrder, self)._prepare_invoice()
#         invoice_vals['payment_method'] = self.payment_method
#         invoice_vals['created_by_id'] = self.created_by_id.id
#         return invoice_vals

from odoo import fields, models, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_method = fields.Selection([
        ('option1', 'نقدى'),
        ('option2', 'اجل'),
    ], string='طريقه الدفع', required=True)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_method = fields.Selection([
        ('option1', 'نقدى'),
        ('option2', 'اجل'),
    ], string='طريقه الدفع', required=True)

    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].browse(vals.get('partner_id'))
        partner.payment_method = vals.get('payment_method')
        return super(SaleOrder, self).create(vals)

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['payment_method'] = self.payment_method
        invoice_vals['created_by_id'] = self.created_by_id.id
        return invoice_vals


