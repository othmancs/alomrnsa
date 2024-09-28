from odoo import models, fields, api
from datetime import date

class EosServiceEnd(models.Model):
    _inherit = 'contract.contract'  # وراثة من نموذج العقود

    eos_employee_name = fields.Char(string='اسم الموظف', required=True)
    eos_start_date = fields.Date(string='تاريخ البداية', required=True)
    eos_end_date = fields.Date(string='تاريخ الانتهاء', required=True)
    eos_salary = fields.Float(string='الراتب الشهري', required=True)
    eos_service_years = fields.Float(string='عدد سنوات الخدمة', compute='_compute_service_years', store=True)
    eos_service_end_compensation = fields.Float(string='تعويض نهاية الخدمة', compute='_compute_service_end_compensation', store=True)

    @api.depends('eos_start_date', 'eos_end_date')
    def _compute_service_years(self):
        for record in self:
            if record.eos_start_date and record.eos_end_date:
                start_date = fields.Date.from_string(record.eos_start_date)
                end_date = fields.Date.from_string(record.eos_end_date)
                record.eos_service_years = (end_date - start_date).days / 365.0
            else:
                record.eos_service_years = 0.0

    @api.depends('eos_service_years', 'eos_salary')
    def _compute_service_end_compensation(self):
        for record in self:
            if record.eos_service_years > 0:
                if record.eos_service_years <= 5:
                    # نصف راتب عن كل سنة من السنوات الخمس الأولى
                    record.eos_service_end_compensation = record.eos_salary / 2 * record.eos_service_years
                else:
                    # راتب عن كل سنة من السنوات بعد الخمس سنوات
                    record.eos_service_end_compensation = (record.eos_salary / 2 * 5) + (record.eos_salary * (record.eos_service_years - 5))
            else:
                record.eos_service_end_compensation = 0.0
