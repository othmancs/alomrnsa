from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrContract(models.Model):
    _inherit = 'hr.contract'

    # إضافة حقل لتوضيح أن العقد تم إنهاؤه
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('close', 'Closed'),
         ('expired', 'Expired')],
        string='Contract Status', default='open')

    def action_end_contract(self):
        for contract in self:
            # التحقق إذا كان العقد في حالة "جاري"
            if contract.state == 'open':
                # التحقق إذا كان الموظف لديه سلفة نشطة
                employee_loans = self.env['hr.employee.loan'].search([
                    ('employee_id', '=', contract.employee_id.id),
                    ('state', '=', 'loaned')
                ])
                if employee_loans:
                    raise ValidationError("The employee has an active loan and cannot end the contract.")

                # التحقق إذا كان الموظف لديه معدات غير مرجعة
                employee_custodies = self.env['hr.employee.custody'].search([
                    ('employee_id', '=', contract.employee_id.id),
                    ('state', '=', 'assigned')
                ])
                if employee_custodies:
                    raise ValidationError("The employee has unreturned equipment and cannot end the contract.")

                # إذا لم توجد سلف أو معدات غير مرجعة، يتم إنهاء العقد
                contract.state = 'expired'
                contract.employee_id.active = False  # تعطيل حساب الموظف بعد انتهاء العقد
                contract.employee_id.resign_date = fields.Date.today()  # إضافة تاريخ الاستقالة
                return True
            else:
                raise ValidationError("The contract is not in 'open' state and cannot be ended.")
