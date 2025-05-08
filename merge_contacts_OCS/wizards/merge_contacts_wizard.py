from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MergeContactsWizard(models.TransientModel):
    _name = 'merge.contacts.wizard'
    _description = 'معالج دمج جهات الاتصال'

    contact_ids = fields.Many2many('res.partner', string='جهات الاتصال للدمج')
    master_contact_id = fields.Many2one('res.partner', string='جهة الاتصال الرئيسية')
    merge_options = fields.Selection([
        ('keep_master', 'الاحتفاظ بجهة الاتصال الرئيسية فقط'),
        ('merge_data', 'دمج البيانات من جميع جهات الاتصال'),
    ], string='خيارات الدمج', default='keep_master')

    @api.model
    def default_get(self, fields):
        res = super(MergeContactsWizard, self).default_get(fields)
        if self._context.get('active_ids'):
            res['contact_ids'] = [(6, 0, self._context['active_ids'])]
        return res

    def action_merge_contacts(self):
        self.ensure_one()
        if len(self.contact_ids) < 2:
            raise UserError(_('يجب تحديد جهتي اتصال على الأقل للدمج.'))
        
        if not self.master_contact_id:
            raise UserError(_('يجب تحديد جهة اتصال رئيسية.'))
        
        if self.master_contact_id not in self.contact_ids:
            raise UserError(_('يجب أن تكون جهة الاتصال الرئيسية من بين جهات الاتصال المحددة للدمج.'))
        
        # دمج جهات الاتصال
        if self.merge_options == 'keep_master':
            # الاحتفاظ بالجهة الرئيسية وإلغاء تنشيط البقية
            (self.contact_ids - self.master_contact_id).write({'active': False})
            
            # نقل العلاقات من الجهات الملغية إلى الجهة الرئيسية
            self._transfer_relations(self.contact_ids - self.master_contact_id, self.master_contact_id)
        else:
            # دمج البيانات من جميع الجهات
            self._merge_all_data(self.contact_ids, self.master_contact_id)
        
        return {
            'type': 'ir.actions.act_window_close',
            'effect': {
                'type': 'rainbow_man',
                'message': _('تم دمج جهات الاتصال بنجاح!')
            }
        }

    def _transfer_relations(self, contacts_to_merge, master_contact):
        """نقل العلاقات من جهات الاتصال الملغية إلى الجهة الرئيسية"""
        # يمكنك إضافة المزيد من النماذج التي لها علاقات مع جهات الاتصال هنا
        relation_models = [
            'sale.order', 'purchase.order', 'account.move', 
            'project.task', 'crm.lead', 'hr.employee'
        ]
        
        for model in relation_models:
            if model in self.env:
                records = self.env[model].search([('partner_id', 'in', contacts_to_merge.ids)])
                records.write({'partner_id': master_contact.id})

    def _merge_all_data(self, contacts, master_contact):
        """دمج البيانات من جميع جهات الاتصال"""
        # دمج العناوين والبريد الإلكتروني وأرقام الهاتف
        emails = []
        phones = []
        mobiles = []
        addresses = []
        
        for contact in contacts:
            if contact.email and contact.email not in emails:
                emails.append(contact.email)
            if contact.phone and contact.phone not in phones:
                phones.append(contact.phone)
            if contact.mobile and contact.mobile not in mobiles:
                mobiles.append(contact.mobile)
            if contact.street and contact.street not in addresses:
                addresses.append(contact.street)
        
        # تحديث البيانات في الجهة الرئيسية
        update_vals = {}
        if emails:
            update_vals['email'] = ', '.join(emails)
        if phones:
            update_vals['phone'] = ', '.join(phones)
        if mobiles:
            update_vals['mobile'] = ', '.join(mobiles)
        if addresses:
            update_vals['street'] = '\n'.join(addresses)
        
        if update_vals:
            master_contact.write(update_vals)
        
        # نقل العلاقات
        self._transfer_relations(contacts - master_contact, master_contact)
        
        # إلغاء تنشيط الجهات الأخرى
        (contacts - master_contact).write({'active': False})