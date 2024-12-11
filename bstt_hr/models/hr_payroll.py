# -*- coding: utf-8 -*-
import babel
import time
from datetime import datetime
from odoo import models, fields, api, tools, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    leave_id = fields.Many2one('hr.leave', string="Leave")
    housing_contract_id = fields.Many2one('hr.contract', string="Housing Allowance")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
            employee = payslip.employee_id
            date_from = payslip.date_from
            date_to = payslip.date_to

            if not self.env.context.get('contract') or not payslip.contract_id:
                contracts = employee._get_contracts(date_from, date_to)

                if not contracts:
                    raise UserError(_("يجب مراجعة بيانات الموظف والتأكد من سريان العقد %s",
                                      employee.name))

                payslip.contract_id = contracts[0]
            # get travel inputs of employee
            payslip.input_line_ids = payslip.get_travel_inputs(contracts, date_from, date_to)
            # get housing allowance of employee
            payslip.input_line_ids = payslip.get_housing_allowance_inputs(contracts, date_from, date_to)

        return super().compute_sheet()

    def get_travel_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip."""
        self.ensure_one()
        res = []
        if contract_ids[0].travel_value > 0:
            contract_obj = self.env['hr.contract']
            emp_id = contract_obj.browse(contract_ids[0].id).employee_id
            leaves = self.env['hr.leave'].search([('employee_id', '=', emp_id.id), ('state', '=', 'validate')])
            for l in leaves:
                # if (date_from <= l.request_date_from <= date_to and not l.is_travel_done) and (not self.input_line_ids.filtered(lambda i: i.leave_id.id == l.id)):
                if (not l.is_travel_done) and (not self.input_line_ids.filtered(lambda i: i.leave_id.id == l.id)):
                    vals = {
                        'input_type_id': self.env.ref('bstt_hr.hr_rule_input_travel').id,
                        'code': 'Travel',
                        'amount': contract_ids[0].travel_value,
                        'leave_id': l.id,
                    }
                    res.append((0, 0, vals))
        return res

    def get_housing_allowance_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip."""
        self.ensure_one()
        res = []
        if contract_ids[0].housing_allowance > 0:
            contract_obj = self.env['hr.contract']
            contract = contract_obj.browse(contract_ids[0].id)
            is_ok = False
            if (contract.house_allowance_months > 0 and contract.housing_allowance > 0) and (not self.input_line_ids.filtered(lambda i: i.housing_contract_id.id == contract.id)):
                if contract.house_allowance_last_date:
                    current_date = contract.house_allowance_last_date + relativedelta(months=contract.house_allowance_months)
                    if date_to.month == current_date.month:
                        is_ok = True
                if not contract.house_allowance_last_date:
                    is_ok = True
                if is_ok:
                    vals = {
                        'input_type_id': self.env.ref('bstt_hr.hr_rule_input_house_allowance').id,
                        'code': self.env.ref('bstt_hr.hr_rule_input_house_allowance').code,
                        'amount': contract_ids[0].housing_allowance,
                        'housing_contract_id': contract.id,
                    }
                    res.append((0, 0, vals))
        return res

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.leave_id:
                line.leave_id.is_travel_done = True
            if line.housing_contract_id:
                line.housing_contract_id.house_allowance_last_date = line.payslip_id.date_to
        return super(HrPayslip, self).action_payslip_done()
