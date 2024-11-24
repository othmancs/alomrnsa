from odoo import models
import logging

_logger = logging.getLogger(__name__)

class BasePartnerMerge(models.TransientModel):
    _inherit = 'base.partner.merge'

    def _validate_contact_count(self, contacts):
        # Log a message when bypassing the restriction
        _logger.info("Merge limit disabled: %d contacts being merged.", len(contacts))
        return
