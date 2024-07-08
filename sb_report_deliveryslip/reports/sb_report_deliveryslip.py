from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def generate_report_data(self, picking_id):
        picking = self.browse(picking_id)
        move_lines = picking.move_lines

        report_data = {
            'picking': picking,
            'move_lines': move_lines,
        }
        return report_data

   

