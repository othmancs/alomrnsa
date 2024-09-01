import logging

from odoo import models, SUPERUSER_ID

_logger = logging.getLogger('base.partner.merge')


class MergePartnerAutomatic(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'

    def _merge(self, partner_ids, dst_partner=None, extra_checks=True):
        _logger.debug(extra_checks)
        super_user = self.env['res.users'].browse(SUPERUSER_ID)
        return super(
            MergePartnerAutomatic, self.with_env(
                self.env(user=super_user, su=True)))._merge(
                    partner_ids=partner_ids, dst_partner=dst_partner,
                    extra_checks=False)
