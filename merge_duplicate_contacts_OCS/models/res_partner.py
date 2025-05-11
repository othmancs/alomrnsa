from odoo import models, fields, api, _
from odoo.exceptions import UserError
from collections import defaultdict


class ResPartner(models.Model):
    _inherit = 'res.partner'

    duplicate_count = fields.Integer('Duplicates', compute='_compute_duplicate_count')
    duplicate_ids = fields.Char('Duplicate IDs', compute='_compute_duplicate_count')

    def _compute_duplicate_count(self):
        for partner in self:
            duplicates = self._find_duplicates(partner)
            partner.duplicate_count = len(duplicates) - 1 if duplicates else 0
            partner.duplicate_ids = ','.join(str(x) for x in duplicates.ids) if duplicates else ''

    def _find_duplicates(self, partner=None):
        """Find duplicates based on name, email and company status"""
        if not partner:
            partner = self

        domain = [
            ('name', '=ilike', partner.name),
            ('is_company', '=', partner.is_company),
            ('id', '!=', partner.id)
        ]

        if partner.email:
            domain.append(('email', '=ilike', partner.email))

        return self.search(domain)

    def action_view_duplicates(self):
        self.ensure_one()
        duplicates = self._find_duplicates()
        return {
            'name': _('Duplicate Contacts'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', duplicates.ids)],
            'context': {'create': False}
        }

    def action_merge_duplicates(self):
        if not self:
            raise UserError(_('Please select at least one record to merge.'))

        duplicates = self._find_duplicates()
        if not duplicates:
            raise UserError(_('No duplicates found for the selected records.'))

        # Merge all duplicates into the first record
        master_partner = duplicates[0]
        duplicates_to_merge = duplicates[1:]

        # Merge all fields from duplicates to master
        for partner in duplicates_to_merge:
            master_partner += partner

        # Archive the duplicates (optional - you can delete them instead)
        duplicates_to_merge.write({'active': False})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%d contacts merged into %s') % (len(duplicates_to_merge), master_partner.name),
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    @api.model
    def find_all_duplicates(self):
        """Find all duplicate contacts in the database"""
        all_partners = self.search([])
        duplicates_dict = defaultdict(list)

        for partner in all_partners:
            key = (partner.name.lower(), partner.email.lower() if partner.email else '', partner.is_company)
            duplicates_dict[key].append(partner.id)

        # Filter only keys with more than one partner
        duplicate_groups = [ids for ids in duplicates_dict.values() if len(ids) > 1]
        return duplicate_groups