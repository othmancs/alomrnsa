from odoo import models, fields, api

class MergeContacts(models.Model):
    _name = 'merge.contacts'
    _description = 'دمج جهات الاتصال'

    type = fields.Selection([
        ('vat', 'الرقم الضريبي'),
        ('name', 'الاسم')
    ], string='نوع التكرار')
    key = fields.Char(string='المفتاح')  # سيكون إما الرقم الضريبي أو الاسم
    count = fields.Integer(string='عدد التكرارات')
    contact_ids = fields.Many2many('res.partner', string='جهات الاتصال المكررة')

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
        
        # حذف السجلات القديمة أولاً
        self.search([]).unlink()
        
        duplicates = []
        
        # إضافة جهات الاتصال المكررة حسب الرقم الضريبي
        for vat, vat_contacts in vat_dict.items():
            if len(vat_contacts) > 1:
                self.create({
                    'type': 'vat',
                    'key': vat,
                    'count': len(vat_contacts),
                    'contact_ids': [(6, 0, [c.id for c in vat_contacts])],
                })
        
        # إضافة جهات الاتصال المكررة حسب الاسم (باستثناء التي تم تضمينها بالفعل حسب الرقم الضريبي)
        for name, name_contacts in name_dict.items():
            if len(name_contacts) > 1:
                # استبعاد جهات الاتصال التي تم تضمينها بالفعل في الرقم الضريبي
                new_contacts = [c for c in name_contacts if not any(
                    c.id in group.contact_ids.ids for group in self.search([('type', '=', 'vat')])
                )]
                if len(new_contacts) > 1:
                    self.create({
                        'type': 'name',
                        'key': name,
                        'count': len(new_contacts),
                        'contact_ids': [(6, 0, [c.id for c in new_contacts])],
                    })
        
        return True
