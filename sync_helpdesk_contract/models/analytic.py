# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _


class AccountAnalyticAccount(models.Model):
    _name = 'account.analytic.account'
    _inherit = 'account.analytic.account'
    _description = 'AccountAnalyticAccount'

    parent_id = fields.Many2one('account.analytic.account', string='Parent Analytic Account')
