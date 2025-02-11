from odoo import models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def delete_with_related_moves(self):
        for partner in self:  # سيتم التعامل مع السجلات التي تم تحديدها
            # البحث عن الحركات المرتبطة بالشريك
            moves = self.env['account.move'].search([('partner_id', '=', partner.id)])
            if moves:
                moves.unlink()

            # حذف الأوامر المرتبطة
            sale_orders = self.env['sale.order'].search([('partner_id', '=', partner.id)])
            if sale_orders:
                sale_orders.unlink()
            
            purchase_orders = self.env['purchase.order'].search([('partner_id', '=', partner.id)])
            if purchase_orders:
                purchase_orders.unlink()

            # حذف المدفوعات المرتبطة
            payments = self.env['account.payment'].search([('partner_id', '=', partner.id)])
            if payments:
                payments.unlink()

            # حذف التحويلات المرتبطة
            stock_pickings = self.env['stock.picking'].search([('partner_id', '=', partner.id)])
            if stock_pickings:
                stock_pickings.unlink()

            # حذف الشريك نفسه
            partner.unlink()

        return True
