# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def action_merge_by_vat(self):
        """
        Merge partners with the same VAT number
        """
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_('You need administrator rights to merge partners!'))
        
        # Find all partners with VAT numbers
        partners_with_vat = self.search([('vat', '!=', False)], order='id asc')
        
        # Group partners by VAT number
        vat_groups = {}
        for partner in partners_with_vat:
            if partner.vat in vat_groups:
                vat_groups[partner.vat].append(partner)
            else:
                vat_groups[partner.vat] = [partner]
        
        # Process groups with more than one partner
        merged_count = 0
        for vat, partners in vat_groups.items():
            if len(partners) > 1:
                # Select the oldest partner as the destination
                destination_partner = partners[0]
                source_partners = partners[1:]
                
                # Merge source partners into destination partner
                self._merge_partners(destination_partner, source_partners)
                merged_count += len(source_partners)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Partners Merged'),
                'message': _('%s duplicate partners were merged based on VAT number.') % merged_count,
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
    
    def _merge_partners(self, destination_partner, source_partners):
        """
        Merge source partners into destination partner
        """
        # Get all models that have partner_id field
        partner_fields = self.env['ir.model.fields'].search([
            ('relation', '=', 'res.partner'),
            ('ttype', '=', 'many2one'),
        ])
        
        for field in partner_fields:
            model = self.env[field.model_id.model]
            if not model._auto:
                continue
            
            try:
                # Find all records pointing to source partners
                records = model.search([(field.name, 'in', source_partners.ids)])
                if records:
                    records.write({field.name: destination_partner.id})
            except Exception as e:
                _logger.warning("Could not merge partner field %s in model %s: %s", 
                               field.name, field.model_id.model, str(e))
        
        # Handle special cases
        self._merge_special_cases(destination_partner, source_partners)
        
        # Archive source partners
        source_partners.write({'active': False})
    
    def _merge_special_cases(self, destination_partner, source_partners):
        """
        Handle special cases that need custom merging logic
        """
        # Merge email and phone information
        emails = set(filter(None, [destination_partner.email] + [p.email for p in source_partners if p.email]))
        phones = set(filter(None, [destination_partner.phone] + [p.phone for p in source_partners if p.phone]))
        mobiles = set(filter(None, [destination_partner.mobile] + [p.mobile for p in source_partners if p.mobile]))
        
        destination_partner.write({
            'email': ', '.join(emails) if emails else False,
            'phone': ', '.join(phones) if phones else False,
            'mobile': ', '.join(mobiles) if mobiles else False,
        })
        
        # Merge addresses
        for source in source_partners:
            if source.child_ids:
                for child in source.child_ids:
                    child.write({'parent_id': destination_partner.id})