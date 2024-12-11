# -*- coding: utf-8 -*-

from odoo import models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        hr_bonus_obj = self.env['hr.bonus']
        hr_deduction_obj = self.env['hr.deduction']
        hr_payslip_input_obj = self.env['hr.payslip.input']
        bonus_input_type = self.env.ref('hr_bonus_deduction.hr_bonus_other_input')
        deduction_input_type = self.env.ref('hr_bonus_deduction.hr_deduction_other_input')

        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
            # get bonuses of employee
            bonuses = hr_bonus_obj.search([('employee_ids', 'in', [payslip.employee_id.id]), ('state', '=', 'approved'),
                                           ('applied_date', '>=', payslip.date_from),
                                           ('applied_date', '<=', payslip.date_to)])

            if bonuses:
                # total bonuses
                total_bonus = sum(bonus.amount for bonus in bonuses)

                bonus_payslip_input = hr_payslip_input_obj.search(
                    [('input_type_id', '=', bonus_input_type.id), ('payslip_id', '=', payslip.id)], limit=1)

                # create new other input if not exists record of bonus rule
                if not bonus_payslip_input:
                    hr_payslip_input_obj.create({
                        'payslip_id': payslip.id,
                        'input_type_id': bonus_input_type.id,
                        'contract_id': payslip.contract_id.id,
                        'amount': total_bonus
                    })
                else:
                    if bonus_payslip_input.amount < total_bonus:
                        bonus_payslip_input.amount = total_bonus

            # get deductions of employee
            deductions = hr_deduction_obj.search(
                [('employee_id', '=', payslip.employee_id.id), ('state', '=', 'approved'),
                 ('applied_date', '>=', payslip.date_from), ('applied_date', '<=', payslip.date_to)])

            if deductions:
                # total deductions
                total_deduction = sum(deduction.amount for deduction in deductions)

                deduction_payslip_input = hr_payslip_input_obj.search(
                    [('input_type_id', '=', deduction_input_type.id), ('payslip_id', '=', payslip.id)])

                # create new other input if not exists record of deduction rule
                if not deduction_payslip_input:
                    hr_payslip_input_obj.create({
                        'payslip_id': payslip.id,
                        'input_type_id': deduction_input_type.id,
                        'contract_id': payslip.contract_id.id,
                        'amount': -total_deduction
                    })
                else:
                    if deduction_payslip_input.amount > -total_deduction:
                        deduction_payslip_input.amount = -total_deduction

        super().compute_sheet()
