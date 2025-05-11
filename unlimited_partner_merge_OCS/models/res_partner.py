from odoo import models, api, _

class PartnerMerge(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'

    def _merge(self, partner_ids, dst_partner=None, extra_checks=True):
        if len(partner_ids) < 2:
            raise ValidationError(_("Please select at least 2 partners to merge."))
        return super()._merge(partner_ids, dst_partner, extra_checks)
