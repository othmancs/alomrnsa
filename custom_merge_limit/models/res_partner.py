from odoo import models, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def merge_contacts(self, contacts):
        # تعديل الحد المسموح
        if len(contacts) > 10:  # تغيير 10 إلى الرقم الذي تريده
            raise UserError("لا يمكنك دمج أكثر من 10 جهات اتصال معاً.")
        # افترض أن هناك منطق الدمج هنا
        # super(ResPartner, self).merge_contacts()
