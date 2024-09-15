from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _update_product_cost(self, product_id, warehouse_id, cost):
        cost_record = self.env['stock.warehouse.product.cost'].search([
            ('product_id', '=', product_id),
            ('warehouse_id', '=', warehouse_id)
        ])
        if cost_record:
            cost_record.write({'cost': cost})
        else:
            self.env['stock.warehouse.product.cost'].create({
                'product_id': product_id,
                'warehouse_id': warehouse_id,
                'cost': cost
            })

    # إضافة الكود المناسب لتحديث التكلفة عند تنفيذ الاستلام
    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        for line in res.move_lines:
            self._update_product_cost(line.product_id.id, res.picking_type_id.warehouse_id.id,
                                      line.product_id.standard_price)
        return res
