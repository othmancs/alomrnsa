from odoo import models, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def merge_contacts(self, contacts):
        # تحقق من عدد جهات الاتصال التي يتم دمجها
        if len(contacts) > 10:  # تغيير 10 إلى الرقم الذي تريده
            raise UserError("لا يمكنك دمج أكثر من 10 جهات اتصال معاً.")
        
        # التحقق من أن جهة الاتصال ليست جزءًا من عناصر أصلية
        for contact in contacts:
            if any(other_contact.id in contact.parent_id.ids for other_contact in contacts):
                raise UserError("لا يمكنك دمج جهة اتصال مع إحدى عناصره الأصلية.")
        
        # منطق الدمج هنا
        return super(ResPartner, self).merge_contacts(contacts)
