from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    created_by_id = fields.Many2one(
        'res.partner', 
        string='أنشئ من قبل', 
        domain="[('branch_id', '=', branch_id)]"
    )

    @api.depends('sale_id')
    def _compute_created_by_id(self):
        for picking in self:
            picking.created_by_id = picking.sale_id.created_by_id if picking.sale_id else False

    created_by_id = fields.Many2one(
        'res.partner', 
        string='أنشئ من قبل', 
        compute='_compute_created_by_id', 
        store=True
    )
