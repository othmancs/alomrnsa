from odoo import models, fields, api

class EmployeeSettlement(models.Model):
    _name = 'employee.settlement'
    _description = 'Employee Settlement'

    name = fields.Char(string='Employee Name', required=True)
    request_date = fields.Date(string='Request Date', required=True)
    residency_id = fields.Char(string='Residency ID')
    nationality = fields.Char(string='Nationality')
    employer = fields.Char(string='Employer')
    settlement_type = fields.Selection([
        ('annual_vacation', 'Annual Vacation'),
        ('final_settlement', 'Final Settlement')
    ], string='Settlement Type', required=True)
    settlement_number = fields.Char(string='Settlement Number')
    total_amount = fields.Float(string='Total Amount')