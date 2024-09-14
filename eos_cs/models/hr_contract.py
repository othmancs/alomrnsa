from odoo import models, fields, api
from datetime import datetime


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # تعريف الحقول المتعلقة بنهاية الخدمة
    service_end_date = fields.Date(string='Service End Date')
    end_of_service_amount = fields.Float(string='End of Service Amount', compute='_compute_end_of_service_amount',
                                         store=True)

    @api.depends('date_end', 'wage')
    def _compute_end_of_service_amount(self):
        for contract in self:
            if contract.date_end and contract.wage:
                # مثال حساب نهاية الخدمة، تأكد من القوانين السعودية الخاصة بك
                contract.end_of_service_amount = self._calculate_service_end_amount(contract.date_end, contract.wage)

    def _calculate_service_end_amount(self, end_date, wage):
        # حساب نهاية الخدمة بناءً على القوانين السعودية
        # تحتاج إلى تعديل هذا الجزء بناءً على القوانين واللوائح الخاصة بنهاية الخدمة في السعودية
        total_days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(self.date_start, '%Y-%m-%d')).days
        months = total_days // 30
        return wage * months * 0.5  # مثال للحساب، يجب تعديله بناءً على القوانين الصحيحة
