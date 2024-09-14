from odoo import models, fields, api
from datetime import date

class HrContract(models.Model):
    _inherit = 'hr.contract'

    service_end_date = fields.Date(string='Service End Date')
    end_of_service_amount = fields.Float(string='End of Service Amount', compute='_compute_end_of_service_amount', store=True)
    
    @api.depends('date_end', 'wage')
    def _compute_end_of_service_amount(self):
        for contract in self:
            if contract.date_end and contract.wage:
                # تعديل الطريقة لحساب نهاية الخدمة
                contract.end_of_service_amount = self._calculate_service_end_amount(contract.date_start, contract.date_end, contract.wage)

    def _calculate_service_end_amount(self, start_date, end_date, wage):
        # تحويل تاريخ البداية والنهاية إلى كائنات datetime.date إذا لزم الأمر
        if isinstance(start_date, str):
            start_date = fields.Date.from_string(start_date)
        if isinstance(end_date, str):
            end_date = fields.Date.from_string(end_date)

        # حساب الفرق بين التواريخ
        total_days = (end_date - start_date).days
        months = total_days // 30

        # تطبيق قواعد نهاية الخدمة
        return wage * months * 0.5  # تعديل الحساب بناءً على القوانين السعودية الخاصة بك
