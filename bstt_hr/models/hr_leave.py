# -*- coding: utf-8 -*-
from odoo import fields, models


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    is_travel_chk = fields.Boolean('يوجد مخصص سفر', default=False)
    is_travel_done = fields.Boolean('تم صرف مخصص السفر', default=False)