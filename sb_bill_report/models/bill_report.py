from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'account.move'

    purchase_name = fields.Char(string='Purchase Name')
    warehouse_name= fields.Char(string='Warehouse Name')
    printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name





