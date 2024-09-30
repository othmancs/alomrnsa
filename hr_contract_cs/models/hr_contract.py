from odoo import models, fields

class HrContract(models.Model):
    _inherit = 'hr.contract'

    end_of_service_report_ids = fields.One2many('hr.end_of_service_report', 'contract_id', string='End of Service Reports')

class HREndOfServiceReport(models.Model):
    _name = 'hr.end_of_service_report'
    _description = 'End of Service Report'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', ondelete='cascade')
    residence_id = fields.Char(string='Residence ID')
    nationality = fields.Char(string='Nationality')
    employer_name = fields.Char(string='Employer Name')
    settlement_number = fields.Char(string='Settlement Number')
    settlement_date = fields.Date(string='Settlement Date')
    total_amount = fields.Float(string='Total Amount')
