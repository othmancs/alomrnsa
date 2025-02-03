from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_view_delivery(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['domain'] = [('origin', '=', self.name)]
        return action
