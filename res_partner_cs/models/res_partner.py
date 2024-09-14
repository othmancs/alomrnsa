from odoo import models, fields, api
from odoo.exceptions import AccessError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit', 'Credit')
    ], string='Customer Type', default='cash')

    @api.model
    def create(self, vals):
        if vals.get('customer_type') == 'credit' and not self.env.user.has_group('your_module.group_credit_customer'):
            raise AccessError("You do not have the necessary permissions to create a Credit customer.")
        return super(ResPartner, self).create(vals)
