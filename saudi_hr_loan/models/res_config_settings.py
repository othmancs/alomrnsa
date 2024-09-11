# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_employee_can_request_loan = fields.Boolean(
        "Employee can Request Loan",
        implied_group="saudi_hr_loan.group_employee_can_request_loan",
    )
