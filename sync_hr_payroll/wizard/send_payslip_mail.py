# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class SendPayslipMail(models.TransientModel):
    _name = "send.payslip.mail"
    _description = "Send Payslip Mail"

    def send_payslip(self):
        draft_payslip = []
        work_email = []
        payslip_ids = self.env['hr.payslip'].browse(self._context.get('active_ids'))
        send_payslip = payslip_ids.filtered(lambda payslip: payslip.state == 'done' and payslip.employee_id.work_email).mapped(lambda payslip: payslip and payslip.send_payslip())
        payslip_ids = payslip_ids.filtered(lambda payslip: payslip.state == 'draft' or not payslip.employee_id.work_email)
        for payslip in payslip_ids:
            if not payslip.employee_id.work_email and payslip.employee_id.name not in work_email:
                work_email.append(payslip.employee_id.name)
            elif payslip.state == 'draft':
                draft_payslip.append(payslip.name)
        if len(work_email) > 0 or len(draft_payslip) > 0:
            for payslip in payslip_ids:
                payslip.draft_payslip_data = ("\n".join(rec for rec in draft_payslip)) or False
                payslip.work_email_data = ("\n".join(rec for rec in work_email)) or False
                return {
                    'name': _("Payslip Details"),
                    'view_mode': 'form',
                    'view_id': self.env.ref('sync_hr_payroll.missing_payslip_details_view').id,
                    'res_model': 'hr.payslip',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'res_id': payslip.id,
                }
