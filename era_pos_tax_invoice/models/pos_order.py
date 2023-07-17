
from odoo import models, fields, api

class POSConfigInherit(models.Model):
    _inherit = 'pos.config'

    allow_qr_code = fields.Boolean(string="Add QR Code in Receipt")

class POSOrder(models.Model):
    _inherit = 'pos.order'

    order_refunded = fields.Char(string="Order Refunded", required=False, )

    @api.model
    def create(self, values):
        res = super(POSOrder, self).create(values)
        print(values)
        if len(res.refunded_order_ids) != 0:
            res.order_refunded = ','.join(res.refunded_order_ids.mapped('pos_reference'))
        print(res.order_refunded)
        return res