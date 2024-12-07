# from odoo import api, fields, models
#
#
# class EmployeePayroll(models.Model):
#     _name = "employee.payroll"
#     _description = 'Employee'
#
#     name = fields.Char(string='Name', required=True)
#     gender = fields.Selection([('Male', 'Male'), ('Female', 'Female')], string='Gender')
#     identification_id = fields.Char(string='Identification ID')
#     department_id = fields.Many2one('custom.payroll.department', string='Department')
#     salary = fields.Float(string='Salary')
#     bank_account = fields.Char(string='Bank Account')
#
# class Department(models.Model):
#     _name = 'custom.payroll.department'
#     _description = 'Department'
#
#     name = fields.Char(string='Name', required=True)
#     manager_id = fields.Many2one('custom.payroll.employee', string='Manager')
#
# class Payroll(models.Model):
#     _name = 'custom.payroll.payroll'
#     _description = 'Payroll'
#
#     employee_id = fields.Many2one('custom.payroll.employee', string='Employee')
#     date = fields.Date(string='Date', required=True)
#     basic_salary = fields.Float(string='Basic Salary')
#     deductions = fields.Float(string='Deductions')
#     net_salary = fields.Float(string='Net Salary', compute='.compute.net.salary')
#
#     @api.depends('basic_salary', 'deductions')
#     def _compute_net_salary(self):
#         for record in self:
#             record.net_salary = record.basic_salary - record.deductions
#

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
class EmployeePayroll(models.Model):
    _name = "employee.payroll"
    _inherit = ['mail.thread']
    _description = 'Employee'

    name = fields.Char(string='Name', required=True, tracking=True)
    gender = fields.Selection([('Male', 'Male'), ('Female', 'Female')], string='Gender', tracking=True)
    identification_id = fields.Char(string='Identification ID', tracking=True)
    department_id = fields.Many2one('custom.payroll.department', string='Department', tracking=True)
    salary = fields.Float(string='Salary', tracking=True)
    bank_account = fields.Char(string='Bank Account', tracking=True)
    capitalized_name = fields.Char(string="Capitalized name", compute="_compute_capitalized_name")
    ref = fields.Char(string="Reference", default=lambda self:_('New'))
    manager_id = fields.Many2one('employee.manager' , string='Manager')
    image_1920 = fields.Image("Image", max_width=1920, max_height=1920)
    avatar_128 = fields.Image("Avatar", max_width=128, max_height=128)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence = self.env['ir.sequence'].next_by_code('employee.payroll')
            # Extract the number part from the sequence and convert it to an integer
            sequence_number = int(sequence.split('HR')[-1])
            # Generate the desired sequence format ('HR00001', 'HR00002', etc.)
            formatted_sequence = 'HR{:05d}'.format(sequence_number)
            vals['ref'] = formatted_sequence
        return super(EmployeePayroll, self).create(vals_list)



    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         vals['ref'] = self.env['ir.sequence'].next_by_code('employee.payroll')
    #     return super(EmployeePayroll, self).create(vals_list)

    # function for pacific things
    # @api.constrains("department_id", "identification_id")
    # def check_ides(self):
    #     for rec in self:
    #         if rec.identification_id and rec.department_id == 0:
    #             raise ValidationError(_("department id & identification_id must be added"))

    @api.depends('name')
    def _compute_capitalized_name(self):
        for rec in self:
            if rec.name:
                rec.capitalized_name = rec.name.upper()
            else:
                rec.capitalized_name = ""


class Department(models.Model):
    _name = 'custom.payroll.department'
    _description = 'Department'

    name = fields.Char(string='Name', required=True)
    manager_id = fields.Many2one('custom.payroll.employee', string='Manager')

class Payroll(models.Model):
    _name = 'custom.payroll.payroll'
    _description = 'Payroll'

    employee_id = fields.Many2one('custom.payroll.employee', string='Employee')
    date = fields.Date(string='Date', required=True)
    basic_salary = fields.Float(string='Basic Salary')
    deductions = fields.Float(string='Deductions')
    net_salary = fields.Float(string='Net Salary', compute='_compute_net_salary')

    @api.depends('basic_salary', 'deductions')
    def _compute_net_salary(self):
        for record in self:
            record.net_salary = record.basic_salary - record.deductions

    # Action for Departments
    def action_department(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Departments',
            'view_mode': 'tree,form',
            'res_model': 'custom.payroll.department',
        }

    # Action for Payrolls
    def action_payroll(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payrolls',
            'view_mode': 'tree,form',
            'res_model': 'custom.payroll.payroll',
        }


