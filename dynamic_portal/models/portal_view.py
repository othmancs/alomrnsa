#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from odoo.addons.base.models.ir_model import FIELD_TYPES
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class PortalView(models.Model):
    _name = 'portal.view'

    list_id = fields.Many2one('portal.portal')
    form_id = fields.Many2one('portal.portal')
    sequence = fields.Integer(default=99)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    field_id = fields.Many2one('ir.model.fields', string="Field", required=True, ondelete='cascade',
                               domain="[('model_id', '=', model_id)]")
    field_name = fields.Char(related='field_id.name')
    required = fields.Boolean()
    readonly = fields.Boolean()
    ttype = fields.Selection(selection=FIELD_TYPES, related='field_id.ttype')
    relation = fields.Char(related='field_id.relation')
    domain = fields.Char()
    attrs_readonly = fields.Char()
    attrs_invisible = fields.Char()
    table_lines = fields.One2many('portal.table.line', 'view_id')


    @api.constrains('domain', 'attrs_readonly', 'attrs_invisible')
    def _check_domain(self):
        eval_context = {
            'uid': self.env.uid,
            'user': self.env.user,
        }
        for rec in self:
            try:
                if rec.domain:
                    safe_eval(rec.domain or '[]', eval_context)
                if rec.attrs_readonly:
                    safe_eval(rec.attrs_readonly or '[]', eval_context)
                if rec.attrs_invisible:
                    safe_eval(rec.attrs_invisible or '[]', eval_context)
            except Exception as e:
                error = "This domain is syntactically not correct:\n %s", e
                raise ValidationError(error)

    def form_view(self):
        return {
            'name': _('Table'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'portal.view',
            'res_id': self.id,
            'view_id': self.env.ref('dynamic_portal.portal_line_form').id,
        }


class PortalTableLine(models.Model):
    _name = 'portal.table.line'

    sequence = fields.Integer(default=99)
    view_id = fields.Many2one('portal.view')
    relation = fields.Char(related='view_id.relation', readonly=False)
    field_id = fields.Many2one('ir.model.fields', string="Field", required=True, ondelete='cascade',
                               domain="[('model_id.model', '=', relation), ('ttype', 'not in', ['binary','one2many'])]")
    ttype = fields.Selection(selection=FIELD_TYPES, related='field_id.ttype')
    required = fields.Boolean()
    readonly = fields.Boolean()
    domain = fields.Char()

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
