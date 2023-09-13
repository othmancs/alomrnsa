from odoo import api, models


class Module(models.Model):
    _inherit = 'ir.module.module'

    def button_update_modules(self):
        return self.button_immediate_upgrade()
