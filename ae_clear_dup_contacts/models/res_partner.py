from odoo import models

class ResPartnerExt(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner'

    def clear_duplicates(self):
        duplicate_contacts = []
        user_obj = self.env['res.users']
        cale_obj = self.env.get('calendar.contacts')  # استخدام get لتجنب الخطأ إذا كان النموذج غير موجود
        for partner in self:
            if partner.email and partner.id not in duplicate_contacts:
                duplicates = self.search([('id', '!=', partner.id), ('email', '=', partner.email)])
                for dup in duplicates:
                    user = user_obj.search([('partner_id', '=', dup.id)])
                    calender = cale_obj.search([('partner_id', '=', dup.id)]) if cale_obj else None
                    if not user and not calender:
                        duplicate_contacts.append(dup.id)
        self.browse(duplicate_contacts).unlink()
