from odoo import models, api, fields
from odoo.exceptions import UserError

class PartnerMergeWizard(models.TransientModel):
    _inherit = 'base.partner.merge'

    # Override the default behavior to allow more than 3 contacts
    @api.model
    def default_get(self, fields_list):
        res = super(PartnerMergeWizard, self).default_get(fields_list)
        return res

    def merge_partners(self):
        # Here you can specify the new limit
        max_merge_limit = 10  # Allow more than 3 contacts; adjust as needed
        if len(self.partner_ids) > max_merge_limit:
            raise UserError(f"لا يمكنك دمج أكثر من {max_merge_limit} جهات اتصال معاً.")
        return super(PartnerMergeWizard, self).merge_partners()
