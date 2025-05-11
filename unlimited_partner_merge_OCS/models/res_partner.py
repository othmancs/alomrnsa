from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def merge(self, partner_ids):
        """ Override the default merge function to remove the 3-partner limit """
        if len(partner_ids) < 2:
            raise ValidationError(_("Please select at least 2 partners to merge."))
        
        # Continue with the original merge logic (without the 3-partner check)
        return super(ResPartner, self).merge(partner_ids)