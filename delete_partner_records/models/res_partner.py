from odoo import models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def unlink(self):
        for partner in self:
            models_to_delete = [
                'account.move',
                'sale.order',
                'purchase.order',
                'account.payment',
                'stock.picking'
            ]
            
            for model in models_to_delete:
                self.env[model].search([('partner_id', '=', partner.id)]).unlink()
        
        return super(ResPartner, self).unlink()