# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = "Res partner Sequences"

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('res.partner') or '/'
        return super(ResPartner, self).create(vals)
