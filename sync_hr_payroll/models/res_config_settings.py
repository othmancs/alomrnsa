# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_account_accountant = fields.Boolean(string='Account Accountant')
    duplicate_payslip_restrict = fields.Boolean(string='Duplicate Payslip Restrict',
                                                config_parameter="sync_hr_payroll.duplicate_payslip_restrict")
