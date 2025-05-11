from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PartnerMergeAutomatic(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'

    def _merge(self, partner_ids, dst_partner=None):
        """ Override the merge function to remove the 3-partner limit """
        if len(partner_ids) < 2:
            raise ValidationError(_("يجب اختيار شريكين على الأقل للدمج."))
        
        # تجاوز التحقق من "أكثر من 3 جهات اتصال"
        return super(PartnerMergeAutomatic, self)._merge(partner_ids, dst_partner)
