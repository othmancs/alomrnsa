from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sales_credit_limit = fields.Float()


