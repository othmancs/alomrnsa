# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel): 
	_inherit = 'res.config.settings'

	allow_warehouse = fields.Boolean(string="Allow Warehouse in Sale Order Line", related='company_id.allow_warehouse', readonly=False)

