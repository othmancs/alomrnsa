from odoo import models, fields, api

class MergeContacts(models.Model):
    _name = 'merge.contacts'
    _description = 'دمج جهات الاتصال'

    @api.model
    def find_duplicate_contacts(self):
        # البحث عن جهات اتصال مكررة بناء على الرقم الضريبي أو الاسم
        contacts = self.env['res.partner'].search([('active', 'in', [True, False])])
        
        # تجميع جهات الاتصال حسب الرقم الضريبي
        vat_dict = {}
        for contact in contacts:
            if contact.vat:
                vat_dict.setdefault(contact.vat, []).append(contact)
        
        # تجميع جهات الاتصال حسب الاسم الكامل
        name_dict = {}
        for contact in contacts:
            name_dict.setdefault(contact.name, []).append(contact)
        
        # تجهيز النتائج
        duplicates = []
        
        # إضافة جهات الاتصال المكررة حسب الرقم الضريبي
        for vat, vat_contacts in vat_dict.items():
            if len(vat_contacts) > 1:
                duplicates.append({
                    'type': 'vat',
                    'key': vat,
                    'contacts': vat_contacts,
                    'count': len(vat_contacts),
                })
        
        # إضافة جهات الاتصال المكررة حسب الاسم (باستثناء التي تم تضمينها بالفعل حسب الرقم الضريبي)
        for name, name_contacts in name_dict.items():
            if len(name_contacts) > 1:
                # استبعاد جهات الاتصال التي تم تضمينها بالفعل في الرقم الضريبي
                new_contacts = [c for c in name_contacts if not any(
                    c in group['contacts'] for group in duplicates if group['type'] == 'vat'
                )]
                if len(new_contacts) > 1:
                    duplicates.append({
                        'type': 'name',
                        'key': name,
                        'contacts': new_contacts,
                        'count': len(new_contacts),
                    })
        
        return duplicates