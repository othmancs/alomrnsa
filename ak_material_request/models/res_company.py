# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    two_step_material_req = fields.Boolean(string="2 step Picking")
