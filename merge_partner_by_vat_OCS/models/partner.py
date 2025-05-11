# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def action_merge_by_vat(self):
        """
        Merge partners with the same VAT number
        """
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_('You need administrator rights to merge partners!'))
        
        # Find all active partners with VAT numbers
        partners_with_vat = self.search([
            ('vat', '!=', False),
            ('active', 'in', [True, False])  # Include inactive partners
        ], order='id asc')
        
        # Group partners by normalized VAT number
        vat_groups = {}
        for partner in partners_with_vat:
            normalized_vat = (partner.vat or '').upper().replace(' ', '')
            if normalized_vat in vat_groups:
                vat_groups[normalized_vat].append(partner)
            else:
                vat_groups[normalized_vat] = [partner]
        
        # Process groups with more than one partner
        merged_count = 0
        for vat, partners in vat_groups.items():
            if len(partners) > 1:
                # Select the oldest active partner as the destination, or oldest inactive if none active
                destination_partner = next((p for p in partners if p.active), partners[0])
                source_partners = [p for p in partners if p != destination_partner]
                
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
        if not source_partners:
            return
            
        # Ensure source_partners is a recordset
        source_partners = self.browse([p.id for p in source_partners])
        
        # Get all models that have partner_id field
        partner_fields = self.env['ir.model.fields'].search([
            ('relation', '=', 'res.partner'),
            ('ttype', '=', 'many2one'),
        ])
        
        for field in partner_fields:
            try:
                model = self.env[field.model_id.model]
                if model._auto:
                    # Find all records pointing to source partners
                    records = model.search([(field.name, 'in', source_partners.ids)])
                    if records:
                        records.write({field.name: destination_partner.id})
            except Exception as e:
                _logger.error("Failed to merge partner field %s in model %s: %s", 
                           field.name, field.model_id.model, str(e))
                continue
        
        # Handle special cases
        self._merge_special_cases(destination_partner, source_partners)
        
        # Archive and clean up source partners
        source_partners.write({
            'active': False,
            'parent_id': destination_partner.id,
            'vat': False,  # Clear VAT to avoid future conflicts
        })

    def _merge_special_cases(self, destination_partner, source_partners):
        """
        Handle special cases that need custom merging logic
        """
        # Merge contact information
        contact_info = {
            'email': ', '.join(filter(None, {destination_partner.email} | {p.email for p in source_partners if p.email})),
            'phone': ', '.join(filter(None, {destination_partner.phone} | {p.phone for p in source_partners if p.phone})),
            'mobile': ', '.join(filter(None, {destination_partner.mobile} | {p.mobile for p in source_partners if p.mobile})),
        }
        destination_partner.write(contact_info)
        
        # Merge addresses and contacts
        for source in source_partners:
            # Move child contacts
            if source.child_ids:
                source.child_ids.write({'parent_id': destination_partner.id})
            
            # Move bank accounts
            if source.bank_ids:
                source.bank_ids.write({'partner_id': destination_partner.id})
