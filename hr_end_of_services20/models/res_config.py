# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2018-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    weekends_per_month = fields.Integer(string='No. of weekends per month',
                                            related='company_id.weekends_per_month',readonly=False)

    salary_structure_id = fields.Many2one('hr.payroll.structure', string='End of service salary structure', 
                                 related='company_id.salary_structure_id',readonly=False)