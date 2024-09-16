# custom_merge_limit/models/res_partner.py

from odoo import models, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def merge_contacts(self):
        # تعديل الحد المسموح
        if len(self) > 10:  # تغيير 10 إلى الرقم الذي تريده
            raise UserError("لا يمكنك دمج أكثر من 10 جهات اتصال معاً.")
        super(ResPartner, self).merge_contacts()
