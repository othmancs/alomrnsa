from odoo import models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
   @api.multi
   def delete_with_related_moves(self):
        for partner in self:
            # البحث عن الحركات المرتبطة بالشريك
            moves = self.env['account.move'].search([('partner_id', '=', partner.id)])
            if moves:
                # حذف الحركات المرتبطة
                moves.unlink()

            # حذف الشريك نفسه
            partner.unlink()

        return True
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
        
