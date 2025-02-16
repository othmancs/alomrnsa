# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PartnerIndustry(models.Model):
    _inherit = "res.partner.industry"

    is_customer = fields.Boolean(string="Is Customer")
    is_vendor = fields.Boolean(string="Is Vendor")
    prefix_code = fields.Char(string="Prefix Code", required="1", copy=False)
    padding = fields.Integer(string="Sequence Size", required="1", default=4)
    next_number = fields.Integer(string="Next Number", default=1, copy=False)

    def _get_sequence_number(self):
        code = ''
        number = ''
        if self.next_number:
            number = str(self.next_number).zfill(self.padding)
        code = str(self.prefix_code) + str(number)
        self.next_number += 1
        return code
