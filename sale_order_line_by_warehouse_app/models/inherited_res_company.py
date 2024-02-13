# -*- coding: utf-8 -*-


from odoo import fields, models

class Company(models.Model):
	_inherit = 'res.company'

	allow_warehouse = fields.Boolean(string="Allow Warehouse in Sale Order Line", default=False)