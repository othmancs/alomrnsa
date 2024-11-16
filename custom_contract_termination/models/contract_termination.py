from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # حقل جديد لتمثيل حالة الإنهاء
    contract_termination_check = fields.Boolean(string='Can Terminate Contract', default=True)

    @api.constrains('contract_termination_check')
    def _check_termination(self):
        for employee in self:
            if not employee.contract_termination_check:
                raise ValidationError(f"لا يمكن إنهاء عقد الموظف {employee.name} لأنه يمتلك عهد مالية أو سلف.")


class HrContractTermination(models.TransientModel):
    _name = 'hr.contract.termination.wizard'
    _description = 'Contract Termination Wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    termination_date = fields.Date(string='Termination Date', required=True)
    reason = fields.Text(string='Reason')

    def confirm_termination(self):
        employee = self.employee_id
        # تحقق إذا كان الموظف لديه عهدة أو سلف مالية
        if self._has_outstanding_liabilities(employee):
            raise ValidationError(f"الموظف {employee.name} لديه عهدة مالية أو سلف لم يتم تسويتها. لا يمكن إنهاء العقد.")

        # إذا لم يكن هناك أي عهد مالية، يمكن إنهاء العقد
        employee.contract_termination_check = False  # منع الإنهاء إذا كانت هناك ذمم مالية
        employee.write({
            'contract_termination_check': False,  # تحديد أن العقد قد تم إنهاؤه
        })
        return {'type': 'ir.actions.act_window_close'}

    def _has_outstanding_liabilities(self, employee):
        # التحقق من وجود أي سلف أو ذمم مالية
        advances = self.env['account.advance'].search([('employee_id', '=', employee.id), ('state', '=', 'open')])
        if advances:
            return True

        debts = self.env['account.debt'].search([('employee_id', '=', employee.id), ('state', '=', 'open')])
        if debts:
            return True

        return False
