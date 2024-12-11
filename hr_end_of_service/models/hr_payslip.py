# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    end_service_id = fields.Many2one('hr.end.service', string='End Of Service', copy=False)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    end_service_id = fields.Many2one('hr.end.service', string='End Of Service', copy=False)

    def compute_sheet(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
            payslip.input_line_ids = payslip.get_eos_inputs()
        return super().compute_sheet()
    
    def get_eos_inputs(self):
        """This Compute the other inputs to employee payslip.
                           """
        res = []

        eos_obj = self.env['hr.end.service'].search([('employee_id', '=', self.employee_id.id),
                                                     ('state', '=', 'approved'),
                                                     ('paid', '=', False)], limit=1)
        if eos_obj:
            if (not self.input_line_ids.filtered(lambda i: i.end_service_id.id == eos_obj.id)):
                vals = {
                    'input_type_id': self.env.ref('hr_end_of_service.hr_rule_input_end_of_service').id,
                    'code': self.env.ref('hr_end_of_service.hr_rule_input_end_of_service').code,
                    'amount': eos_obj.eos_total,
                    'end_service_id': eos_obj.id,
                }
                res.append((0, 0, vals))
        return res

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.end_service_id:
                line.end_service_id.paid = True
        return super(HrPayslip, self).action_payslip_done()
