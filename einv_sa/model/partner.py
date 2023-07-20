#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning


class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"
    building_no = fields.Char(string="Building no", help="Building No")
    district = fields.Char(string="District", help="District")
    code = fields.Char(string="Code", help="Code")
    additional_no = fields.Char(string="Additional no", help="Additional No")
    other_id = fields.Char(string="Other ID", help="Other ID")

    def test(self):

        pass
