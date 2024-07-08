from odoo import models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for rec in self:
            for picking in rec.picking_ids:
                picking.partner_ref = rec.partner_ref
        return res
