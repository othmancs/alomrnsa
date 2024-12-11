#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from odoo.addons.base.models.ir_model import FIELD_TYPES
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

class PortalViewButton(models.Model):
    _name = 'portal.view.button'

    portal_id = fields.Many2one('portal.portal')
    sequence = fields.Integer(default=99)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    name = fields.Char(required=True,)
    action = fields.Char(required=True,)
    type = fields.Selection([('object', 'Object'), ('action', 'Action')], default='object')
    attrs_invisible = fields.Char()
    field_id = fields.Many2one('ir.model.fields', string="Field", ondelete='cascade',
                               domain="[('model_id', '=', model_id), ('ttype', 'not in', ['binary','many2many'])]")

    @api.constrains('attrs_invisible')
    def _check_domain(self):
        eval_context = {
            'uid': self.env.uid,
            'user': self.env.user,
        }
        for rec in self:
            try:
                safe_eval(rec.attrs_invisible or '[]', eval_context)
            except Exception as e:
                error = "This domain is syntactically not correct:\n %s", e
                raise ValidationError(error)

