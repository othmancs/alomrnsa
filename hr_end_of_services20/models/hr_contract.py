# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    eos_payslip_id = fields.Many2one('hr.payslip', string="Payslip")
    work_years = fields.Float(String='Work Years',readonly=True,compute ='_compute_working')
    end_service = fields.Boolean(string = "End service")
    reason_id = fields.Many2one('hr.end.service.reason', string="Reason",)
    eos_structure_id = fields.Many2one('hr.payroll.structure', string="EOS Salary structure", default= lambda self: self.env['res.company']._company_default_get().salary_structure_id.id,)

    weekends_per_month = fields.Integer(string='No. of weekends per month',
                                            related='company_id.weekends_per_month',
                                            readonly=False)
    @api.depends
    def _compute_working(self): 
        from_date= False
        if self.date_start and self.date_end:

          from_date = fields.Date.from_string(self.date_start)
          end_date = fields.Date.from_string(self.date_end)
          self.work_years =  (end_date - from_date).days / 365.25


    
    def employee_end_service(self):
        payroll_payslip=self.env['hr.payslip']
        result ={}
        for rec in self:
            rec.write({'date_end':datetime.now().date()})
            rec.employee_id.write({'leave_date':datetime.now().date()})
            data={
                'employee_id': rec.employee_id.id,
                'date_from': rec.date_start,
                'date_to': rec.date_end,
                'contract_id':rec.id,
                'struct_id': rec.eos_structure_id.id or False,
                }
            payslip_rec=payroll_payslip.create(data)
            if payslip_rec:
                rec.write({'eos_payslip_id':payslip_rec.id})
                action = self.env.ref('hr_payroll.action_view_hr_payslip_form')
                result = action.read()[0]
                result['views'] = [(self.env.ref('hr_payroll.view_hr_payslip_form').id, 'form')]
                result['res_id'] = payslip_rec.id
                result['context'] = {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'}
        return result



    
    def eos_payslip_action(self):
        action = self.env.ref('hr_payroll.action_view_hr_payslip_form')
        result = action.read()[0]
        payroll_payslip=self.env['hr.payslip']
        for rec in self:
            
            #if payslip_rec:
            #    rec.write({'eos_payslip_id': payslip_rec.id})
            #result['domain'] = str([('id', '=', payslip_rec.id)])
            result['views'] = [(self.env.ref('hr_payroll.view_hr_payslip_form').id, 'form')]
            result['res_id'] = rec.eos_payslip_id.id
        return result
       


