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
from odoo import models, api, fields, Command


class PayslipOverTime(models.Model):
    _inherit = 'hr.payslip'

    overtime_ids = fields.Many2many('hr.overtime')

    @api.model
    def _compute_input_line_ids(self):
        """
        function used for writing overtime record in payslip
        input tree.

        """
        input_data = []
        res = super(PayslipOverTime, self)._compute_input_line_ids()
        overtime_type = self.env.ref('tct_overtime_update.hr_salary_rule_overtime')
        overtime_input_type = self.env.ref('tct_overtime_update.input_overtime_payroll')
        contract = self.contract_id
        overtime_id = self.env['hr.overtime'].search([('employee_id', '=', self.employee_id.id),
                                                      ('contract_id', '=', self.contract_id.id),
                                                      ('state', '=', 'approved'), ('payslip_paid', '=', False)])
        hrs_amount = overtime_id.mapped('cash_hrs_amount')
        day_amount = overtime_id.mapped('cash_day_amount')
        cash_amount = sum(hrs_amount) + sum(day_amount)
        old_input_rec = self.input_line_ids.filtered(lambda r: r.input_type_id.id == overtime_input_type.id)
        if old_input_rec:
            print(old_input_rec)
            for rec in old_input_rec:
                self.input_line_ids = [(2, rec.id, 0)]
        if overtime_id and self.struct_id and overtime_input_type in self.struct_id.input_line_type_ids:
            self.overtime_ids = overtime_id
            input_data.append(Command.create({
                'name': overtime_type.name,
                'amount': cash_amount,
                'input_type_id': overtime_input_type.id if overtime_input_type else 1
            }))
            # input_data = {
            #     'name': overtime_type.name,
            #     'code': overtime_type.code,
            #     'amount': cash_amount,
            #     'contract_id': contract.id,
            #     'input_type_id': self.env.ref('tct_overtime_update.input_overtime_payroll').id if self.env.
            #     ref('tct_overtime_update.input_overtime_payroll').id else 1
            # }
            # res.append(input_data)
            print(input_data)
            self.update({'input_line_ids': input_data})
        return res

    def action_payslip_done(self):
        """
        function used for marking paid overtime
        request.

        """
        for recd in self.overtime_ids:
            if recd.type == 'cash':
                recd.payslip_paid = True
        return super(PayslipOverTime, self).action_payslip_done()
