from odoo import api, fields, models
from odoo.exceptions import ValidationError

class EmployeeManager(models.Model):
    _name = "employee.manager"
    _inherit = "mail.thread"
    _description = "Manager Record"

    name = fields.Char(string="Name", required=True, tracking=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender', required=True, tracking=True)
    department_id = fields.Many2one('custom.payroll.department', string='Department', tracking=True)
    email = fields.Char(string="Email", tracking=True)
    address = fields.Text(string="Address", tracking=True)
    birthdate = fields.Date(string="Birthdate")
    phone = fields.Char(string="Phone Number", required=True, tracking=True)
    active = fields.Boolean(default=True)



    @api.constrains('phone')
    def _check_phone_number(self):
        for rec in self:
            if rec.phone and not rec.phone.isdigit():
                raise ValidationError("Phone number must contain only numeric characters.")

