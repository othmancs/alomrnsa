# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MRLine(models.Model):
    _inherit = "material.request.line"

    seq = fields.Integer(string="التسلسل", required=False, )



