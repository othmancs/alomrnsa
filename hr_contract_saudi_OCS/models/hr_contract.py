from odoo import models, fields, api
from datetime import datetime


class HrContract(models.Model):
    _inherit = 'hr.contract'

    notice_days = fields.Integer(string="أيام الإشعار", default=30)
    trial_period = fields.Integer(string="فترة التجربة (أيام)", default=90)
    work_location = fields.Char(string="Work Location")
    # def print_contract(self):
    #     return self.env.ref('hr_contract_saudi.report_employee_contract').report_action(self)
    def print_contract(self):
        self.ensure_one()
        return self.env.ref('hr_contract_saudi_OCS.employee_contract_report').report_action(self)

        
    def get_contract_duration(self):
        for contract in self:
            if contract.date_start and contract.date_end:
                delta = contract.date_end - contract.date_start
                return delta.days // 365
        return 1

    def get_arabic_date(self, date_str):
        if not date_str:
            return ""
        date_obj = fields.Date.from_string(date_str)
        months = {
            1: "يناير",
            2: "فبراير",
            3: "مارس",
            4: "أبريل",
            5: "مايو",
            6: "يونيو",
            7: "يوليو",
            8: "أغسطس",
            9: "سبتمبر",
            10: "أكتوبر",
            11: "نوفمبر",
            12: "ديسمبر"
        }
        return f"{date_obj.day} {months[date_obj.month]} {date_obj.year}"
