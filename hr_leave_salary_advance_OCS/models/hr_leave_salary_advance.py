from odoo import models, fields, api


class HrLeaveSalaryAdvance(models.Model):
    _name = 'hr.leave.salary.advance'
    _description = 'مخالصة الإجازة السنوية كراتب'

    employee_id = fields.Many2one('hr.employee', string='الموظف', required=True)
    department_id = fields.Many2one('hr.department', string='القسم', related='employee_id.department_id', store=True)
    job_id = fields.Many2one('hr.job', string='المسمى الوظيفي', related='employee_id.job_id', store=True)
    leave_type_id = fields.Many2one('hr.leave.type', string='نوع الإجازة', required=True,
                                    default=lambda self: self.env.ref('hr_leave_salary_advance.annual_leave_type'))
    available_leaves = fields.Float(string='رصيد الإجازة المتاح', compute='_compute_available_leaves')
    requested_days = fields.Float(string='عدد الأيام المطلوبة', required=True)
    amount = fields.Float(string='المبلغ', compute='_compute_amount', store=True)
    currency_id = fields.Many2one('res.currency', string='العملة', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('approved', 'معتمدة'),
        ('paid', 'مسددة'),
        ('refused', 'مرفوضة')], string='الحالة', default='draft', tracking=True)
    date = fields.Date(string='التاريخ', default=fields.Date.today)
    payment_id = fields.Many2one('account.payment', string='سند الصرف', readonly=True)
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)

    @api.depends('employee_id', 'leave_type_id')
    def _compute_available_leaves(self):
        for record in self:
            if record.employee_id and record.leave_type_id:
                record.available_leaves = record.employee_id._get_remaining_leaves(record.leave_type_id)
            else:
                record.available_leaves = 0

    @api.depends('requested_days', 'employee_id')
    def _compute_amount(self):
        for record in self:
            if record.employee_id and record.requested_days > 0 and record.employee_id.contract_id:
                daily_wage = record.employee_id.contract_id.wage / 30
                record.amount = daily_wage * record.requested_days
            else:
                record.amount = 0

    def action_approve(self):
        for record in self:
            if record.requested_days > record.available_leaves:
                raise UserError("لا يمكن الموافقة على الطلب لأن الأيام المطلوبة أكثر من الرصيد المتاح")
        self.write({'state': 'approved'})
        return True

    def action_pay(self):
        AccountPayment = self.env['account.payment']
        for record in self:
            if not record.employee_id.address_home_id:
                raise UserError("يجب تحديد عنوان منزلي للموظف لإنشاء سند الصرف")

            payment = AccountPayment.create({
                'payment_type': 'outbound',
                'partner_id': record.employee_id.address_home_id.id,
                'amount': record.amount,
                'currency_id': record.currency_id.id,
                'date': fields.Date.today(),
                'ref': f'مخالصة إجازة لـ {record.employee_id.name}',
                'journal_id': self.env['account.journal'].search([('type', '=', 'cash')], limit=1).id,
            })

            record.write({
                'state': 'paid',
                'payment_id': payment.id
            })

            # Deduct leaves from employee's balance
            record.employee_id._deduct_leaves(record.leave_type_id, record.requested_days)
        return True

    def action_refuse(self):
        self.write({'state': 'refused'})
        return True

    def action_draft(self):
        self.write({'state': 'draft'})
        return True