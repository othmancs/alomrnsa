# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class EquipmentInspectionForm(models.Model):
    _name = 'equipment.inspection.form'
    _description = 'Equipment Inspection Form'

    name = fields.Char(string='Name', required=True, translate=True)
    inspection_form_no = fields.Char(string='Inspenction Form No.', translate=True)
    inspection_form_version_no = fields.Char(string='Inspection Form Version No.', translate=True)
    equipment_company_id = fields.Many2one('res.company', string='Company')
    equipment_category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category')
    department_id = fields.Many2one('hr.department', string='Department')
    schedule_selection = fields.Selection([('annually', 'Annually'), ('monthly', 'Monthly'), ('weekly', 'Weekly'),
                                        ('daily', 'Daily'), ('hourly', 'Hourly'), ('preshift', 'Pre-Shift'),
                                        ('postshift', 'Post-Shift')], string='Schedule', translate=True)
    equipment_inspection_form_line_ids = fields.One2many('equipment.inspection.form.line', 'inspection_form_id', string='Form Lines')
    submitted_inspections_form_ids = fields.One2many('equipment.submit.inspection', 'equipment_form_id', string='Submitted Forms')


class EquipmentInspectionFormLine(models.Model):
    _name = 'equipment.inspection.form.line'
    _description = 'Equipment Inspection Form Line'
    _order = 'sequence'

    inspection_form_id = fields.Many2one('equipment.inspection.form', string='Form')
    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Name', required=True)


class EquipmentRunInspenction(models.Model):
    _name = 'equipment.run.inspection'
    _description = 'Equipment Run Inspection'

    name = fields.Char(string='Name', required=True)
    equipment_form_id = fields.Many2one('equipment.inspection.form', string='Form')
    employee_id = fields.Many2one('hr.employee', string='Inspector', required=True)
    shift_id = fields.Many2one('hr.shift', string='Shift')
    odometer_reading = fields.Char(string='Odometer Reading')
    department_id = fields.Many2one('hr.department', string='Department')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    scanned_barcode = fields.Char(string='Barcode')
    date = fields.Date(string='Date', default=fields.Date.today())
    inspection_selection = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string='Inspection')
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('not_submitted', 'Not Submitted')], default='draft')
    run_inspenction_line_ids = fields.One2many('equipment.run.inspection.line', 'run_inspection_id', string='Inspection Lines')

    def action_submit(self):
        self.state = 'submitted'
        submit_lines = [(0, 0, {'name': line.name, 'inspection_selection': line.inspection_selection, 'description': line.description}) for line in self.run_inspenction_line_ids]
        self.equipment_id.submitted_inspections_ids = [(0, 0, {'employee_id': self.employee_id.id,
                                                            'status': self.inspection_selection,
                                                            'shift_id': self.shift_id.id,
                                                            'odometer_reading': self.odometer_reading,
                                                            'submit_date': fields.Date.today(),
                                                            'equipment_form_id': self.equipment_form_id.id,
                                                            'submitted_inspection_line_ids': submit_lines})]
        return True


class EquipmentRunInspenctionLine(models.Model):
    _name = 'equipment.run.inspection.line'
    _description = 'Equipment Run Inspection Line'

    run_inspection_id = fields.Many2one('equipment.run.inspection', string='Inspection')
    name = fields.Char(string='Name')
    inspection_selection = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string='Inspection', required=True)
    description = fields.Text(string='Description')


class EquipmentSubmittedInspection(models.Model):
    _name = 'equipment.submit.inspection'
    _description = 'Equipment Sumbit Inspection'
    _rec_name = 'equipment_id'

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    employee_id = fields.Many2one('hr.employee', string='Inspector')
    shift_id = fields.Many2one('hr.shift', string='Shift')
    odometer_reading = fields.Char(string='Odometer Reading')
    status = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string='Status')
    submit_date = fields.Date(string='Submit Date', default=fields.Date.today())
    equipment_form_id = fields.Many2one('equipment.inspection.form', string='Form')
    submitted_inspection_line_ids = fields.One2many('equipment.submit.inspection.line', 'submit_inspection_id', string='Submitted Lines')


class EquipmentSubmitInspenctionLine(models.Model):
    _name = 'equipment.submit.inspection.line'
    _description = 'Equipment Submit Inspection Line'

    submit_inspection_id = fields.Many2one('equipment.submit.inspection', string='Inspection')
    name = fields.Char(string='Name')
    inspection_selection = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string='Inspection', required=True)
    description = fields.Text(string='Description')
