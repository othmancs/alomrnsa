from odoo import models, fields

class Employee(models.Model):
    _inherit = 'hr.employee'

    end_date = fields.Date(string="End Date")
    service_years = fields.Float(string="Service Years", compute="_compute_service_years")
    eos_amount = fields.Float(string="End of Service Amount", compute="_compute_eos_amount")

    def _compute_service_years(self):
        for record in self:
            if record.end_date:
                delta = record.end_date - record.date_start
                record.service_years = delta.days / 365

    def _compute_eos_amount(self):
        for record in self:
            # حساب مبلغ نهاية الخدمة بناءً على القوانين السعودية
            if record.service_years <= 5:
                record.eos_amount = record.service_years * record.contract_id.wage * 0.5
            else:
                record.eos_amount = (5 * record.contract_id.wage * 0.5) + ((record.service_years - 5) * record.contract_id.wage)
