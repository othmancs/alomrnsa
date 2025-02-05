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
                duplicates.pop(0)  # إزالة السجل الأساسي من القائمة
                main_partner._merge_data(duplicates)

    def _merge_data(self, duplicate_partners):
        for duplicate in duplicate_partners:
            # نقل البيانات المرتبطة (مثال: الفواتير، المبيعات، الاتصالات)
            self._transfer_related_data(duplicate)
            duplicate.unlink()

    def _transfer_related_data(self, duplicate):
        """نقل جميع البيانات المرتبطة إلى السجل الأساسي قبل الحذف"""
        related_models = [
            ('sale.order', 'partner_id'),
            ('account.move', 'partner_id'),
            ('res.users', 'partner_id'),
        ]

        for model, field in related_models:
            records = self.env[model].search([(field, '=', duplicate.id)])
            records.write({field: self.id})

        # تحديث الحقول الفارغة فقط (مثل الهاتف، البريد الإلكتروني)
        if not self.phone and duplicate.phone:
            self.phone = duplicate.phone
        if not self.email and duplicate.email:
            self.email = duplicate.email
