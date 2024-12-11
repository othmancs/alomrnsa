# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import format_date


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    category_ids = fields.Many2many('hr.employee.category', groups="hr.group_hr_manager", string='الوسوم')

    @api.depends('category_ids')
    @api.onchange('category_ids')
    def _compute_employee_ids_according_category(self):
        for wizard in self:
            domain = wizard._get_available_contracts_domain()
            if wizard.category_ids:
                domain = expression.AND([
                    domain,
                    [('category_ids', 'in', self.category_ids.ids)]
                ])
            wizard.employee_ids = self.env['hr.employee'].search(domain)
