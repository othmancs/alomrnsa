# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, api, fields, _
import time
from dateutil.relativedelta import relativedelta


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        payslip_line_obj = self.env['salary.installment.line']
        slip_line_obj = self.env['hr.payslip.line']
        skip_installment_obj = self.env['skip.salary.installment']
        for payslip in self:
            advance_salary_ids = self.env['hr.advance.salary'].search(['|', '&', ('payment_start_date', '>=', payslip.date_from),
                                                                    ('payment_start_date', '<=', payslip.date_to),
                                                                    ('payment_start_date', '<=', payslip.date_from),
                                                                    ('employee_id', '=', payslip.employee_id.id),
                                                                    ('state', 'in', ['approve2', 'paid'])])
            for rec in advance_salary_ids:
                skip_installment_ids = skip_installment_obj.search(
                    [('advance_salary_id', '=', rec.id), ('state', '=', 'approve'), ('date', '>=', payslip.date_from),
                     ('date', '<=', payslip.date_to)])
                if skip_installment_ids:
                    if rec.payment_end_date:
                        due_date = rec.payment_end_date + relativedelta(months=1)
                        rec.write({'payment_end_date': due_date})
                else:
                    slip_line_ids = slip_line_obj.search([('slip_id', '=', payslip.id),
                                                          ('code', '=', 'ADV/SAL' + str(rec.id))])
                    if slip_line_ids:
                        amount = slip_line_ids.read(['total'])[0]['total']
                        payslip_line_data = {
                            'advance_salary_id': rec.id,
                            'payslip_id': payslip.id,
                            'employee_id': payslip.employee_id.id,
                            'amount': amount if payslip.credit_note else abs(amount),
                            'date': time.strftime('%Y-%m-%d')
                        }
                        payslip_line_obj.create(payslip_line_data)
                        rec.amount_paid += abs(amount)
                        if rec.amount_paid == rec.request_amount:
                            rec.write({'state': 'done'})
                            rec.action_mail_send(self)
        return res

    def advance_salary_deduction(self):
        slip_line_obj = self.env['hr.payslip.line']
        skip_installment_obj = self.env['skip.salary.installment']
        for payslip in self:
            advance_salary_ids = self.env['hr.advance.salary'].search(['|', '&', ('payment_start_date', '>=', payslip.date_from),
                                                                    ('payment_start_date', '<=', payslip.date_to),
                                                                    ('payment_start_date', '<=', payslip.date_from),
                                                                    ('employee_id', '=', payslip.employee_id.id),
                                                                    ('state', 'in', ['approve2', 'paid'])])
            rule_ids = self.env['hr.salary.rule'].search([('code', '=', 'ADV/SAL')])
            if rule_ids:
                rule = rule_ids[0]
                oids = slip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'ADV/SAL')])
                if oids:
                    oids.unlink()
                for rec in advance_salary_ids:
                    skip_installment_ids = skip_installment_obj.search([('advance_salary_id', '=', rec.id),
                                                                        ('state', '=', 'approve'),
                                                                        ('date', '>=', payslip.date_from),
                                                                        ('date', '<=', payslip.date_to)])
                    if not skip_installment_ids:
                        amount = rec.deduction_amount if rec.payment == 'partially' else rec.amount_to_pay
                        slip_line_data = {
                                'slip_id': payslip.id,
                                'salary_rule_id': rule.id,
                                'contract_id': payslip.contract_id.id,
                                'name': rule.name,
                                'code': 'ADV/SAL' + str(rec.id),
                                'category_id': rule.category_id.id,
                                'sequence': rule.sequence + rec.id,
                                'appears_on_payslip': rule.appears_on_payslip,
                                'amount': -amount,
                            }
                        if abs(slip_line_data['amount']) > rec.amount_to_pay:
                            slip_line_data.update({'amount': -rec.amount_to_pay})
                        slip_line_obj.create(slip_line_data)
                        net_ids = slip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'NET')])
                        if net_ids:
                            net_record = net_ids[0]
                            net_ids.write({'amount': net_record.amount + slip_line_data['amount']})

    def compute_sheet(self):
        """
            Override method for calculate advance salary on payslip calculation time
        """
        res = super(HrPayslip, self).compute_sheet()
        for payslip in self:
            payslip.advance_salary_deduction()
        return res
