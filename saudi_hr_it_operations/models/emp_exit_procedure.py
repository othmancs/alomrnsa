# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ExitType(models.Model):
    _name = 'emp.exit.type'
    _description = 'Exit Type'

    name = fields.Char(string='Name')


class ExitProcedure(models.Model):
    _name = 'emp.exit.procedure'
    _inherit = 'mail.thread'
    _description = "Employee Exit Procedure"
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    employee_code = fields.Char(related='employee_id.code', string='Employee Clock #')
    exit_type = fields.Many2one('emp.exit.type', string='Exit Type', copy=False)
    uniform_returned = fields.Selection([('yes', 'Yes'), ('no', 'NO'), ('not_applicable', 'N/A')],
        string='Uniforms Returned?', copy=False)
    equipment_returned = fields.Selection([('yes', 'Yes'), ('no', 'NO'), ('not_applicable', 'N/A')],
        string='Equipment Returned?', copy=False)
    hire_date = fields.Date(string='Hire Date', copy=False, related="employee_id.date_of_join")
    last_date = fields.Date(string='Last Date', copy=False)
    rehire = fields.Boolean(string='Rehire?', copy=False)
    manager_notes = fields.Text(string='Comments', copy=False)

    generated_roe = fields.Boolean(string='Generated ROE?')
    terminate_in_bv = fields.Boolean(string='Terminate in BV')
    accounting_notes = fields.Text(string='Notes/Comments', copy=False)

    deduction_uniforms = fields.Boolean(string='Deduction/ Uniforms?')
    deduction_tools = fields.Boolean(string='Deduction/Tools etc?')
    vacation_pay = fields.Boolean(string='Vacation pay Issued?')
    final_cheque = fields.Boolean(string='Final Cheque Issued?')
    cancel_benefits = fields.Boolean(string='Cancel Benefits')

    edit_training_matrix = fields.Boolean(string='Edit Training Matrix')
    edit_employee_count_report = fields.Boolean(string='Edit Employeee Count Report')
    edit_employee_tracker = fields.Boolean(string='Edit Employee# Tracker')
    plant_wage_tracker = fields.Boolean(string='Plant Emp. Eval/Wage Tracker')
    individual_wage_tracker = fields.Boolean(string='Individual Plant Emp. Eval/Wage Tracker')
    obsolete_emp_in_hr_drive = fields.Boolean(string='Obsolete Employee File in HR Drive')
    edit_bday_list = fields.Boolean(string='Edit Birthday List')
    remove_from_calendar = fields.Boolean(string='Remove from Calendar')
    edit_attendance_tracking = fields.Boolean(string='Edit Attendance Tracking Matrix')
    deactivate_pdf = fields.Boolean(string='Deactivate PDF')
    deactivate_email = fields.Boolean(string='Deactivate Email')
    obtain_company_keys = fields.Boolean(string='Obtain Company Keys')
    obtain_company_phone = fields.Boolean(string='Obtain Company Phone')
    hr_notes = fields.Text(string='Notes/Comments', copy=False)

    equipment_ids = fields.Many2many('maintenance.equipment', 'equipment_exit_id', string='Equipments')

    state = fields.Selection([('draft', 'Draft'),
        ('plant_approved', 'Plant Manager Approved'),
        ('accounting_approved', 'Accounting Approved'),
        ('hr_payroll_approved', 'HR Payroll Approved'),
        ('hr_manager_approved', 'HR Manager Approved'),
        ('cancel', 'Cancelled')], string='Status', default='draft', tracking=True)

    def action_plant_approved(self):
        for rec in self:
            rec.state = 'plant_approved'

    def action_accounting_approved(self):
        for rec in self:
            rec.state = 'accounting_approved'

    def action_payroll_approved(self):
        for rec in self:
            rec.state = 'hr_payroll_approved'

    def action_hr_manager_approved(self):
        for rec in self:
            rec.state = 'hr_manager_approved'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.onchange('employee_id')
    def get_equipments(self):
        self.equipment_ids = [(5, )]
        if self.employee_id:
            request_ids = self.env['maintenance.equipment.request'].search([('employee_id', '=', self.employee_id.id), ('state', 'in', ['approve'])])
            equipment_ids = request_ids.mapped('equipment_id').ids or []
            self.equipment_ids = [(6, 0, equipment_ids)]
