#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from odoo.addons.base.models.ir_model import FIELD_TYPES


class PortalAccess(models.Model):
    _name = 'portal.access'

    portal_id = fields.Many2one('portal.portal')
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string="User", required=True)
    allow_read = fields.Boolean(default=True)
    allow_write = fields.Boolean(default=True)
    allow_create = fields.Boolean(default=True)
    allow_delete = fields.Boolean(default=True)
