from odoo import models, fields, api

class EmpExitWizard(models.TransientModel):
    _name = 'emp.exit.wizard'
    _description = 'Employee Exit Wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
        # start_date = fields.Date(string='Start Date')  # تأكد من أن هذا الحقل موجود

    exit_date = fields.Date(string='Exit Date', required=True, default=fields.Date.today)
    notes = fields.Text(string='Notes')

    def confirm_exit(self):
        # Logic for confirming employee exit
        if self.employee_id:
            self.employee_id.contract_id.write({'state': 'close'})
            # Additional logic as needed, e.g., notifications or updates
            return {'type': 'ir.actions.client', 'tag': 'reload'}
