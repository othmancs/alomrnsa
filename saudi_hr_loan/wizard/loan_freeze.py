# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class FreezeEmployeeLoan(models.TransientModel):
    _name = "freeze.employee.loan"
    _description = "Freeze Employee Loan"

    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)

    def action_ok_button(self):
        hr_loan = self.env["hr.loan"].browse(self.env.context.get("active_id"))
        hr_loan.is_loan_freeze_button_action()
        hr_loan.start_date = self.end_date
