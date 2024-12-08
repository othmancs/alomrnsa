# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2018-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class ResCompany(models.Model):
    _inherit = 'res.company'

    weekends_per_month = fields.Integer(string='No. of weekends per month ', default=4)
    salary_structure_id = fields.Many2one('hr.payroll.structure', string='End of service salary structure')
