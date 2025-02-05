from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def merge_similar_contacts(self):
        partners = self.search([])
        grouped_partners = {}

        for partner in partners:
            key = (partner.name.strip().lower(), partner.vat or '')
            if key not in grouped_partners:
                grouped_partners[key] = []
            grouped_partners[key].append(partner)

        for key, duplicates in grouped_partners.items():
            if len(duplicates) > 1:
                main_partner = duplicates[0]
                for duplicate in duplicates[1:]:
                    main_partner |= duplicate
                main_partner._merge_data(duplicates[1:])

    def _merge_data(self, duplicate_partners):
        for duplicate in duplicate_partners:
            duplicate.unlink()
