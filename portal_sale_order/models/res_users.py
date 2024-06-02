from odoo import fields, models, api
from odoo.tools.sql import column_exists, create_column


class ResUsers(models.Model):
    _inherit = 'res.users'

    cannot_edit_unit_price = fields.Boolean('عدم تعديل السعر')
