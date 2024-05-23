from odoo import fields, models, api


class Website(models.Model):
    _inherit = 'website'

    def _prepare_sale_order_values(self, partner_sudo):
        default_branch = self.env['res.branch'].sudo().search([
            ('is_default', '=', True),
        ], limit=1)
        values = super(Website, self)._prepare_sale_order_values(partner_sudo)
        if default_branch:
            values['branch_id'] = default_branch.id
        return values
