from odoo import models, fields, api

class HREmployee(models.Model):
    _inherit = 'hr.employee'  # توسيع موديول الموظفين الموجود

    @api.model_create_multi
    def create(self, vals_list):
        """
        عند إنشاء موظف جديد، يتم إنشاء جهة اتصال له تلقائيًا.
        """
        employees = super().create(vals_list)
        for employee in employees:
            self._create_employee_partner(employee)
        return employees

    def _create_employee_partner(self, employee):
        """
        دالة مساعدة لإنشاء جهة اتصال للموظف.
        """
        Partner = self.env['res.partner']
        partner = Partner.create({
            'name': employee.name,
            'email': employee.work_email,
            'phone': employee.work_phone,
            'mobile': employee.mobile_phone,
            'company_id': employee.company_id.id,
            'type': 'contact',  # نوع جهة الاتصال
            'active': True,
        })
        employee.write({'partner_id': partner.id})  # ربط الموظف بجهة الاتصال

    def write(self, vals):
        """
        عند تحديث بيانات الموظف، يتم تحديث جهة الاتصال المرتبطة به.
        """
        res = super().write(vals)
        for employee in self:
            if not employee.partner_id:
                self._create_employee_partner(employee)
            else:
                employee.partner_id.write({
                    'name': employee.name,
                    'email': employee.work_email,
                    'phone': employee.work_phone,
                    'mobile': employee.mobile_phone,
                })
        return res