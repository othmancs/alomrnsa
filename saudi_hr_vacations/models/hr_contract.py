# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HRContract(models.Model):
    _inherit = "hr.contract"

    vacation_allocation_ids = fields.One2many(
        "hr.vacations.allocation", "contract_id", string="Vacation Allocation"
    )


class HREmployee(models.Model):
    _inherit = "hr.employee"

    vacation_allocation_ids = fields.One2many(
        "hr.vacations.allocation", "employee_id", string="Vacation Allocation"
    )
