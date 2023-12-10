# -*- coding: utf-8 -*-

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    custody_approval_route = fields.Selection(
        selection=[
            ('no', 'No'),
            ('optional', 'Optional'),
            ('required', 'Required')
        ], string="Use Approval Route", default='no')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    custody_approval_route = fields.Selection(related='company_id.custody_approval_route',
                                               string="Use Approval Route", readonly=False)

