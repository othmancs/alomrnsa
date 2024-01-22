# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################
from datetime import datetime
from odoo import models, api, _


class SalaryRuleInputInherit(models.Model):
    _inherit = 'hr.payslip'

    def input_data_salary_line(self, name, amount):
        input_type = self.env['hr.payslip.input.type'].search([
            ('input_id', '=', name)])
        for data in self:
            data.write({
                'input_line_ids': [(0, 0, {
                    'input_type_id': input_type,
                    'amount': amount
                })],
            })

    @api.onchange('struct_id', 'date_from', 'date_to', 'employee_id')
    def onchange_employee_salary(self):
        res = super(SalaryRuleInputInherit, self).onchange_employee_loan()
        salary_line = self.struct_id.rule_ids.filtered(
                        lambda x: x.code == 'SAR')
        if salary_line:
            get_amount = self.env['salary.advance'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'approve')
            ])
            if get_amount:
                if self.date_from <= get_amount.date <= self.date_to:
                    amount = get_amount.advance
                    name = salary_line.id
                    date = get_amount.date
                    code = salary_line.code
                    if code not in self.input_line_ids.mapped('input_type_id').mapped('code'):
                        self.input_data_salary_line(name, amount)
        return res
