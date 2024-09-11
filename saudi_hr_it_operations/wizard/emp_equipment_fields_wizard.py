# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields
import base64
from odoo.tools import groupby


class EmpEquipmentFieldsWizard(models.TransientModel):
    _name = 'emp.equipment.fields.wizard'
    _description = "Emp Equipment Fields Wizard"

    employee_registraion_id = fields.Many2one('hr.employee.registration', string='Employee Registraion')
    equipment_fields_line_wizard_ids = fields.One2many('emp.equipment.fields.line.wizard', 'wizard_id', string='Lines')

    def confirm(self):
        equipment_list = [(5,)]
        for line in self.equipment_fields_line_wizard_ids:
            equipment_list.append((0, 0, {'equipment_registration_id': line.equipment_registration_id.id,
                                        'question_name': line.question_name,}))
                                        # 'answer': line.answer}))
        data = {}
        for equipment_registration, wizard_lines in groupby(self.equipment_fields_line_wizard_ids, lambda elid: elid.equipment_registration_id):
            list_equipment = []
            for equipment in wizard_lines:
                list_equipment.append(equipment.question_name)
            data.update({equipment_registration.product_id.name: list_equipment})
        attachment_list = []
        report = self.env['ir.actions.report']._get_report_from_name('saudi_hr_it_operations.report_template_hr_agreement')
        if report.print_report_name:
            report_name = safe_eval(report.print_report_name, {'object': self.employee_registraion_id})
        elif report.attachment:
            report_name = safe_eval(report.attachment, {'object': self.employee_registraion_id})
        else:
            report_name = 'HR Agreement'
        filename = "%s.%s" % (report_name, "pdf")
        report_template_agreement, unused_filetype = self.env.ref('saudi_hr_it_operations.report_template_hr_agreement')._render_qweb_pdf([self.employee_registraion_id.id], data={'equipment_data': data})
        attachment = self.env['ir.attachment'].create({
                'name': filename,
                'datas': base64.b64encode(report_template_agreement),
                'res_model': 'hr.employee.registration',
                'res_id': self.employee_registraion_id.id,
                'type': 'binary',
            })
        attachment_list.append(attachment.id)

        report = self.env['ir.actions.report']._get_report_from_name('saudi_hr_it_operations.report_template_intake_equipments')
        if report.print_report_name:
            report_name = safe_eval(report.print_report_name, {'object': self.employee_registraion_id})
        elif report.attachment:
            report_name = safe_eval(report.attachment, {'object': self.employee_registraion_id})
        else:
            report_name = 'IT Request Form'
        filename = "%s.%s" % (report_name, "pdf")
        report_template_agreement, unused_filetype = self.env.ref('saudi_hr_it_operations.report_template_intake_equipments')._render_qweb_pdf([self.employee_registraion_id.id])
        attachment = self.env['ir.attachment'].create({
                'name': filename,
                'datas': base64.b64encode(report_template_agreement),
                'res_model': 'hr.employee.registration',
                'res_id': self.employee_registraion_id.id,
                'type': 'binary',
            })
        attachment_list.append(attachment.id)

        self.employee_registraion_id.write({'employee_equipments_fields_ids': equipment_list})
        # ('saudi_hr_it_operations.report_hr_agreement')
        try:
            template_id = self.env.ref('saudi_hr_it_operations.email_template_intake_equipments_it_operations').id
        except ValueError:
            template_id = False

        ctx = {
            'default_model': 'hr.employee.registration',
            'default_res_id': self.employee_registraion_id.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True,
            'default_attachment_ids': [(6, 0, attachment_list)]
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'context': ctx,
            'target': 'new',
        }
        # return True


class EmpEquipmentFieldsLineWizard(models.TransientModel):
    _name = 'emp.equipment.fields.line.wizard'
    _description = "Emp Equipment Fields Line Wizard"
    
    wizard_id = fields.Many2one('emp.equipment.fields.wizard', string='Equipments')
    equipment_registration_id = fields.Many2one('equipment.registration', string='Equipment')
    question_name = fields.Char(string='Question')
    # answer = fields.Char(string='Answer')
