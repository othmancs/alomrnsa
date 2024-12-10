from odoo import models, fields, api, exceptions
from datetime import datetime
from odoo.tools.translate import _


class ESReportrWizard(models.TransientModel):
    _name = "hr.end.service.benefit.wizard"
    _description = "Ending Service Reward Report Wizard"

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", )

    def action_print(self):
        self.ensure_one()
        [data] = self.read()
        employee_id = self.env['hr.employee'].search([('id', '=', self.read(['employee_id'])[0]['employee_id'][0])])
        rewards_ids = self.env['hr.end.service.benefit'].search([('employee_id', '=', employee_id.id)])
        print(rewards_ids.ids)
        datas = {
            'ids': rewards_ids,
            'model': 'hr.end.service.benefit',
            'form': data,
            'employee_id': employee_id.name
        }
        return self.env.ref('hr_end_service_benefits.report_hr_es_action').with_context(
            from_transient_model=True).report_action(rewards_ids, data=datas)


        # data = {}
        # data['form'] = self.read(['employee_id'])[0]
        # records = self.env['hr.employee'].search([('id', '=', self.read(['employee_id'])[0])])
        # dates = [False, False]
        # docargs = {
        #     'doc_ids': records.mapped('id'),
        #     'doc_model': 'hr.end.service.benefit.wizard',
        #     'docs': records,
        #     'dates': dates,
        # }
        # report = self.env.ref('hr_end_service_benefits.report_hr_es_action').report_action(self, data=data)
        # print(2222222222222)
        # return report


class ReportESReport(models.AbstractModel):
    _name = 'report.hr_end_service_benefits.report_hr_es_action'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('hello innnn')
        records = self.env['hr.employee'].search([('id', '=', data['form']['employee_id'][0])])
        dates = [False, False]
        if len(records) > 0:
            docargs = {
                'doc_ids': records.mapped('id'),
                'doc_model': 'hr.end.service.benefit',
                'docs': records,
                'dates': dates,
            }
            return self.env['report'].render('hr_end_service_benefits.report_ending_service', docargs)
        else:
            raise exceptions.Warning(_("There is no employee to show"))
