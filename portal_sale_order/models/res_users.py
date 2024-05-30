from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    cannot_edit_unit_price = fields.Boolean()
