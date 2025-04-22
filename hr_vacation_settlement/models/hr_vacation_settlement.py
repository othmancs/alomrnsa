# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'
    
    is_paid = fields.Boolean(
        string='إجازة مدفوعة',
        default=True,
        help='إذا تم تحديده، تعتبر الإجازة مدفوعة الأجر'
    )

class HrVacationSettlement(models.Model):
    _name = 'hr.vacation.settlement'
    _description = 'تصفية الإجازة السنوية'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc'

    # الحقول الأساسية
    name = fields.Char(string='الرقم المرجعي', readonly=True, default='New')
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='القسم', related='employee_id.department_id', store=True)
    job_id = fields.Many2one('hr.job', string='الوظيفة', related='employee_id.job_id', store=True)
    date_from = fields.Date(string='من تاريخ', required=True, default=fields.Date.today, tracking=True)
    date_to = fields.Date(string='إلى تاريخ', required=True, default=fields.Date.today, tracking=True)
    
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirmed', 'تم التأكيد'),
        ('approved', 'تم الاعتماد'),
        ('done', 'منتهي'),
        ('canceled', 'ملغي')
    ], string='الحالة', default='draft', tracking=True)
    
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', string='العملة', related='company_id.currency_id', store=True)
    notes = fields.Text(string='ملاحظات')

    # حقول حساب الإجازة
    total_vacation_days = fields.Float(string='إجمالي أيام الإجازة', compute='_compute_leave_days', store=True)
    paid_leave_days = fields.Float(string='أيام الإجازة المدفوعة', compute='_compute_leave_days', store=True)
    unpaid_leave_days = fields.Float(string='أيام الإجازة غير المدفوعة', compute='_compute_leave_days', store=True)
    used_vacation_days = fields.Float(string='إجمالي الأيام المستخدمة', compute='_compute_leave_days', store=True)
    remaining_vacation_days = fields.Float(string='الأيام المتبقية', compute='_compute_leave_days', store=True)
    
    daily_wage = fields.Monetary(string='الأجر اليومي', compute='_compute_daily_wage', store=True)
    vacation_amount = fields.Monetary(string='مبلغ تصفية الإجازة', compute='_compute_vacation_amount', store=True)

    # حقول السلف
    advance_ids = fields.One2many('hr.vacation.advance', 'settlement_id', string='سلف الإجازة')
    total_advances = fields.Monetary(string='إجمالي السلف', compute='_compute_total_advances', store=True)
    net_amount = fields.Monetary(string='الصافي المستحق', compute='_compute_net_amount', store=True)

    # إجراءات العمل
    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_('لا يمكن تأكيد تصفية الإجازة إلا في حالة المسودة.'))
            record.write({
                'state': 'confirmed',
                'confirmed_by': self.env.user.id,
                'confirmed_date': fields.Datetime.now()
            })

    def action_approve(self):
        for record in self:
            if record.state != 'confirmed':
                raise UserError(_('لا يمكن اعتماد تصفية الإجازة إلا بعد التأكيد.'))
            record.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now()
            })

    def action_done(self):
        for record in self:
            if record.state != 'approved':
                raise UserError(_('لا يمكن إنهاء تصفية الإجازة إلا بعد الاعتماد.'))
            record.write({'state': 'done'})

    def action_cancel(self):
        for record in self:
            record.write({'state': 'canceled'})

    def action_draft(self):
        for record in self:
            record.write({'state': 'draft'})

    # الحسابات
    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_leave_days(self):
        for record in self:
            # القيم الافتراضية
            record.total_vacation_days = 30  # حسب النظام السعودي
            record.paid_leave_days = 0
            record.unpaid_leave_days = 0
            record.used_vacation_days = 0
            record.remaining_vacation_days = 30

            if not record.employee_id or not record.date_from or not record.date_to:
                continue

            # البحث عن جميع الإجازات المعتمدة
            all_leaves = self.env['hr.leave'].search([
                ('employee_id', '=', record.employee_id.id),
                ('state', '=', 'validate'),
                ('request_date_from', '>=', record.date_from),
                ('request_date_to', '<=', record.date_to)
            ])

            # تصنيف الإجازات
            for leave in all_leaves:
                if leave.holiday_status_id.is_paid:
                    record.paid_leave_days += leave.number_of_days
                else:
                    record.unpaid_leave_days += leave.number_of_days

            # حساب الإجماليات
            record.used_vacation_days = record.paid_leave_days + record.unpaid_leave_days
            record.remaining_vacation_days = max(0, record.total_vacation_days - record.used_vacation_days)

    @api.depends('employee_id')
    def _compute_daily_wage(self):
        for record in self:
            if not record.employee_id:
                record.daily_wage = 0
                continue
            
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', record.employee_id.id),
                ('state', '=', 'open')
            ], limit=1)
            
            record.daily_wage = contract.wage / 30 if contract else 0

    @api.depends('advance_ids.amount')
    def _compute_total_advances(self):
        for record in self:
            record.total_advances = sum(advance.amount for advance in record.advance_ids)

    @api.depends('vacation_amount', 'total_advances')
    def _compute_net_amount(self):
        for record in self:
            record.net_amount = record.vacation_amount - record.total_advances

    @api.depends('remaining_vacation_days', 'daily_wage')
    def _compute_vacation_amount(self):
        for record in self:
            record.vacation_amount = record.remaining_vacation_days * record.daily_wage

    # قيود النموذج
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from > record.date_to:
                raise UserError(_('تاريخ البداية يجب أن يكون قبل تاريخ النهاية.'))

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.vacation.settlement') or 'New'
        return super(HrVacationSettlement, self).create(vals)


class HrVacationAdvance(models.Model):
    _name = 'hr.vacation.advance'
    _description = 'سلف الإجازة'

    name = fields.Char(string='الوصف', required=True)
    date = fields.Date(string='التاريخ', default=fields.Date.today)
    amount = fields.Monetary(string='المبلغ', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='العملة', related='settlement_id.currency_id', store=True)
    settlement_id = fields.Many2one('hr.vacation.settlement', string='تصفية الإجازة', ondelete='cascade')
    notes = fields.Text(string='ملاحظات')

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise UserError(_('يجب أن يكون مبلغ السلف أكبر من الصفر.'))
