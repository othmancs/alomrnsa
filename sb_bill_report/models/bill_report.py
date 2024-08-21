from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'account.move'

    purchase_name = fields.Char(string='Purchase Name')
    warehouse_name= fields.Char(string='Warehouse Name')





