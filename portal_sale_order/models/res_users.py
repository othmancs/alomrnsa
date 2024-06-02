from odoo import fields, models, api
from odoo.tools.sql import column_exists, create_column


class ResUsers(models.Model):
    _inherit = 'res.users'

    cannot_edit_unit_price = fields.Boolean('عدم تعديل السعر')

    def _auto_init(self):
        # Skip the computation of the field `livechat_operator_id` at the module installation
        # We can assume no livechat operator attributed to visitor if it was not installed
        if not column_exists(self.env.cr, "res_users", "cannot_edit_unit_price"):
            create_column(self.env.cr, "res_users", "cannot_edit_unit_price", "bool")
        return super()._auto_init()
