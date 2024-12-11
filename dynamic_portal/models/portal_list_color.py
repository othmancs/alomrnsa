#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from odoo.addons.base.models.ir_model import FIELD_TYPES
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class PortalListColor(models.Model):
    _name = 'portal.list.color'

    portal_id = fields.Many2one('portal.portal')
    color = fields.Selection(
        selection=[('green', 'Green'),
                   ('orange', 'Orange'), ],
        required=True)
    domain = fields.Char(required=True)

    @api.constrains('domain')
    def _check_domain(self):
        eval_context = {
            'uid': self.env.uid,
            'user': self.env.user,
        }
        for rec in self:
            try:
                safe_eval(rec.domain or '[]', eval_context)
            except Exception as e:
                error = "This domain is syntactically not correct:\n %s", e
                raise ValidationError(error)
