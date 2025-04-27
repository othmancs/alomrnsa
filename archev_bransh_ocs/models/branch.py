from odoo import models, fields

class MultiBranch(models.Model):
    _inherit = 'multi.branch'

    active = fields.Boolean(default=True)
