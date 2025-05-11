# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def action_merge_by_vat(self):
        """
        Merge partners with the same VAT number (Memory optimized version)
        """
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_('You need administrator rights to merge partners!'))
        
        # Process in batches to avoid memory issues
        batch_size = 1000
        merged_count = 0
        
        # Find all VAT numbers with duplicates
        self.env.cr.execute("""
            SELECT vat, COUNT(id) 
            FROM res_partner 
            WHERE vat IS NOT NULL AND vat != ''
            GROUP BY vat 
            HAVING COUNT(id) > 1
            ORDER BY vat
        """)
        
        for vat, count in self.env.cr.fetchall():
            # Get partners for this VAT in batches
            offset = 0
            while True:
                partners = self.search([
                    ('vat', '=', vat)
                ], offset=offset, limit=batch_size, order='id asc')
                
                if not partners:
                    break
                
                # Process this batch
                if len(partners) > 1:
                    destination = partners[0]
                    sources = partners[1:]
                    self._merge_partners(destination, sources)
                    merged_count += len(sources)
                    self.env.cr.commit()  # Commit after each batch
                
                offset += batch_size
        
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
    
    def _merge_partners(self, destination, sources):
        """
        Memory-optimized merge of partners
        """
        if not sources:
            return

        # Process in smaller chunks
        chunk_size = 100
        for i in range(0, len(sources), chunk_size):
            chunk = sources[i:i+chunk_size]
            
            # 1. Handle related records
            self._merge_related_records(destination, chunk)
            
            # 2. Merge contact info
            self._merge_contact_info(destination, chunk)
            
            # 3. Archive sources
            chunk.write({
                'active': False,
                'parent_id': destination.id,
                'vat': False,
            })
            self.env.cr.commit()  # Commit after each chunk
    
    def _merge_related_records(self, destination, sources):
        """
        Merge related records in memory-efficient way
        """
        # Get all models with partner_id field
        partner_fields = self.env['ir.model.fields'].search([
            ('relation', '=', 'res.partner'),
            ('ttype', '=', 'many2one'),
        ])
        
        for field in partner_fields:
            try:
                model = self.env[field.model_id.model]
                if model._auto:
                    # Process records in batches
                    offset = 0
                    while True:
                        records = model.search([
                            (field.name, 'in', sources.ids)
                        ], offset=offset, limit=100)
                        
                        if not records:
                            break
                            
                        records.write({field.name: destination.id})
                        offset += 100
                        self.env.cr.commit()
                        
            except Exception as e:
                _logger.error("Merge failed for model %s: %s", field.model_id.model, str(e))
                continue
    
    def _merge_contact_info(self, destination, sources):
        """
        Merge contact information efficiently
        """
        # Collect unique values
        emails = {destination.email}
        phones = {destination.phone}
        mobiles = {destination.mobile}
        
        for partner in sources:
            if partner.email: emails.add(partner.email)
            if partner.phone: phones.add(partner.phone)
            if partner.mobile: mobiles.add(partner.mobile)
        
        # Update destination
        update_vals = {}
        if emails: update_vals['email'] = ', '.join(filter(None, emails))
        if phones: update_vals['phone'] = ', '.join(filter(None, phones))
        if mobiles: update_vals['mobile'] = ', '.join(filter(None, mobiles))
        
        if update_vals:
            destination.write(update_vals)
