from odoo import fields, models


class MaterialRequest(models.Model):
    _inherit = 'material.request'

    created_by_id = fields.Many2one('res.partner', string='انشأ من قبل', domain="[('branch_id', '=', branch_from_id)]")

