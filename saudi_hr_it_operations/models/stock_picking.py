# -*- coding: utf-8 -*-

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    employee_registration_id = fields.Many2one('hr.employee.registration', string='Employee Asset Registrations')
