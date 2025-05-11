from odoo import models, api, _
from odoo.exceptions import ValidationError

class PartnerMerge(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'

    def _merge(self, partner_ids, dst_partner=None, extra_checks=True):
        if len(partner_ids) < 2:
            raise ValidationError(_("يجب اختيار شريكين على الأقل للدمج."))
        return super()._merge(partner_ids, dst_partner, extra_checks)

    def action_merge(self):
        self.ensure_one()
        if len(self.partner_ids) < 2:
            raise ValidationError(_("يجب اختيار شريكين على الأقل للدمج."))
        return super().action_merge()
