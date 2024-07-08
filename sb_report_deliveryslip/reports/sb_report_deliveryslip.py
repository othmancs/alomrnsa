from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    print_by = fields.Char(string='انشا بواسطه',compute='_compute_print_by')

    def _compute_print_by(self):
        for rec in self:
            rec.print_by = self.env.user.name

    @api.model
    def generate_report_data(self, picking_id):
        picking = self.browse(picking_id)
        move_lines = picking.move_lines
        user= self.env.user.name

        report_data = {
            'picking': picking,
            'move_lines': move_lines,
        }
        return report_data
