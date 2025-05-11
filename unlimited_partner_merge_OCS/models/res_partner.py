from odoo import models, api, _

class PartnerMergeAutomatic(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'

    def _merge(self, partner_ids, dst_partner=None, extra_checks=True):
        """ Override merge function to remove 3-partner limit and handle new parameters """
        if len(partner_ids) < 2:
            raise ValidationError(_("يجب اختيار شريكين على الأقل للدمج."))
        
        # استدعاء الدالة الأصلية مع جميع المعاملات المطلوبة
        return super(PartnerMergeAutomatic, self)._merge(
            partner_ids,
            dst_partner=dst_partner,
            extra_checks=extra_checks
        )
