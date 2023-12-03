from odoo import models, fields, api, _


class HrJob(models.Model):
    _inherit = 'product.product'

    is_property = fields.Boolean('Property', tracking=True)



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'

    is_property = fields.Boolean(related='product_id.is_property',string='Property', store=False, readonly=False, tracking=True)

