from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def generate_report_data(self, order_id):
        order = self.browse(order_id)
        order_lines = order.order_line

        report_data = {
            'order': order,
            'order_lines': order_lines,
        }
        return report_data

   

