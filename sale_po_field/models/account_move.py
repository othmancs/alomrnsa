from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    purchase_order_number = fields.Char(string='رقم أمر الشراء', readonly=True)

    def _auto_init(self):
        """ Ensure purchase_order_number is copied from sale order. """
        res = super()._auto_init()
        self.env.cr.execute("""
            UPDATE account_move am
            SET purchase_order_number = so.purchase_order_number
            FROM sale_order so
            WHERE am.invoice_origin = so.name
            AND so.purchase_order_number IS NOT NULL
        """)
        return res
