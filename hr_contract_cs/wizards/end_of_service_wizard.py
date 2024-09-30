from odoo import models, fields, api

class EndOfServiceWizard(models.TransientModel):
    _name = 'end.of_service.wizard'
    _description = 'Wizard to generate End of Service report'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)

    def generate_report(self):
        # Trigger the Excel report generation
        return self.env.ref('hr_contract.end_of_service_xlsx').report_action(self)
