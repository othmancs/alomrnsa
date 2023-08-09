from odoo import api, models, fields
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime, timedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vendor_rating = fields.Float(readonly=True)
