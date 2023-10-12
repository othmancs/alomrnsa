from odoo import api, fields, models, _

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    is_store = fields.Boolean()

    def get_name_and_address(self):
        res = []
        for warehouse in self:
            address = warehouse.partner_id and \
                warehouse.partner_id._display_address(True) or ''
            res.append({
                'id': warehouse.id,
                'name': warehouse.name,
                'address': address,
                'partner_id': warehouse.partner_id.id
            })
        return res
