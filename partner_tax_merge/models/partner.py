from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.model
    def _merge(self, partner_ids, dst_partner=None):
        if len(partner_ids) < 2:
            return False
            
        if not dst_partner:
            dst_partner = self.browse(partner_ids[0])
            partner_ids = partner_ids[1:]
            
        Partner = self.env['res.partner']
        Partner._merge_process(partner_ids, dst_partner)
        self._merge_invoices(partner_ids, dst_partner)
        return True
    
    def _merge_invoices(self, partner_ids, dst_partner):
        Invoice = self.env['account.move']
        for partner_id in partner_ids:
            invoices = Invoice.search([('partner_id', '=', partner_id)])
            if invoices:
                invoices.write({'partner_id': dst_partner.id})
        return True
