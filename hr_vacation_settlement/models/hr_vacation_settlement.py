# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime
import logging

_logger = logging.getLogger(__name__)

class HrVacationSettlement(models.Model):
    _name = 'hr.vacation.settlement'
    _description = 'تصفية الإجازة السنوية'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc'

    # الحقول الأساسية
    name = fields.Char(string='الرقم المرجعي', readonly=True, default='New')
    employee_id = fields.Many2one(
        'hr.employee', string='الموظف',
        required=True, tracking=True
    )
    department_id = fields.Many2one(
        'hr.department', string='القسم',
        related='employee_id.department_id', store=True
    )
    job_id = fields.Many2one(
        'hr.job', string='الوظيفة',
        related='employee_id.job_id', store=True
    )
    date_from = fields.Date(
        string='من تاريخ', required=True,
        default=fields.Date.today, tracking=True
    )
    date_to = fields.Date(
        string='إلى تاريخ', required=True,
        default=fields.Date.today, tracking=True
    )
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirmed', 'تم التأكيد'),
        ('approved', 'تم الاعتماد'),
        ('done', 'منتهي'),
        ('canceled', 'ملغي')
    ], string='الحالة', default='draft', tracking=True)
    company_id = fields.Many2one(
        'res.company', string='الشركة',
        default=lambda self: self.env.company, required=True
    )
    currency_id = fields.Many2one(
        'res.currency', string='العملة',
        related='company_id.currency_id', store=True
    )

    # حقول حساب الإجازة
    total_vacation_days = fields.Float(
        string='إجمالي أيام الإجازة',
        compute='_compute_vacation_days', store=True
    )
    used_vacation_days = fields.Float(
        string='أيام الإجازة المستخدمة',
        compute='_compute_vacation_days', store=True
    )
    remaining_vacation_days = fields.Float(
        string='أيام الإجازة المتبقية',
        compute='_compute_vacation_days', store=True
    )
    vacation_amount = fields.Monetary(
        string='مبلغ تصفية الإجازة',
        compute='_compute_vacation_amount', store=True
    )
    daily_wage = fields.Monetary(
        string='الأجر اليومي',
        compute='_compute_daily_wage', store=True
    )

    # حقول السلف
    advance_ids = fields.One2many(
        'hr.vacation.advance', 'settlement_id',
        string='سلف الإجازة'
    )
    total_advances = fields.Monetary(
        string='إجمالي السلف',
        compute='_compute_total_advances', store=True
    )
    net_amount = fields.Monetary(
        string='الصافي المستحق',
        compute='_compute_net_amount', store=True
    )

    # حقول الموافقة
    confirmed_by = fields.Many2one(
        'res.users', string='تم التأكيد بواسطة',
        readonly=True, copy=False
    )
    confirmed_date = fields.Datetime(
        string='تاريخ التأكيد',
        readonly=True, copy=False
    )
    approved_by = fields.Many2one(
        'res.users', string='تم الاعتماد بواسطة',
        readonly=True, copy=False
    )
    approved_date = fields.Datetime(
        string='تاريخ الاعتماد',
        readonly=True, copy=False
    )
    notes = fields.Text(string='ملاحظات')

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
    def _compute_vacation_days(self):
        for record in self:
            if not record.employee_id or not record.date_from or not record.date_to:
                record.total_vacation_days = 0
                record.used_vacation_days = 0
                record.remaining_vacation_days = 0
                continue

            # حساب إجمالي أيام الإجازة المستحقة حسب سياسة الشركة
            total_days = 30  # مثال: 30 يوم إجازة سنوية حسب نظام العمل السعودي
            
            # حساب أيام الإجازة المستخدمة في الفترة
            leaves = self.env['hr.leave'].search([
                ('employee_id', '=', record.employee_id.id),
                ('state', '=', 'validate'),
                ('holiday_status_id.is_vacation', '=', True),
                ('date_from', '>=', record.date_from),
                ('date_to', '<=', record.date_to)
            ])
            
            used_days = sum(leave.number_of_days for leave in leaves)
            
            record.total_vacation_days = total_days
            record.used_vacation_days = used_days
            record.remaining_vacation_days = total_days - used_days

    @api.depends('employee_id', 'daily_wage', 'remaining_vacation_days')
    def _compute_vacation_amount(self):
        for record in self:
            if not record.employee_id or not record.remaining_vacation_days:
                record.vacation_amount = 0
                continue
            
            record.vacation_amount = record.daily_wage * record.remaining_vacation_days

    @api.depends('employee_id')
    def _compute_daily_wage(self):
        for record in self:
            if not record.employee_id:
                record.daily_wage = 0
                continue
            
            # حساب الأجر اليومي حسب نظام العمل السعودي
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', record.employee_id.id),
                ('state', '=', 'open')
            ], limit=1)
            
            if contract:
                # الأجر اليومي = الراتب الأساسي / 30 يوم حسب نظام العمل السعودي
                record.daily_wage = contract.wage / 30
            else:
                record.daily_wage = 0

    @api.depends('advance_ids.amount')
    def _compute_total_advances(self):
        for record in self:
            record.total_advances = sum(advance.amount for advance in record.advance_ids)

    @api.depends('vacation_amount', 'total_advances')
    def _compute_net_amount(self):
        for record in self:
            record.net_amount = record.vacation_amount - record.total_advances

    # دالة إنشاء الرقم المرجعي
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.vacation.settlement') or 'New'
        return super(HrVacationSettlement, self).create(vals)

    # قيود النموذج
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from > record.date_to:
                raise UserError(_('تاريخ البداية يجب أن يكون قبل تاريخ النهاية.'))

    @api.constrains('remaining_vacation_days')
    def _check_remaining_days(self):
        for record in self:
            if record.remaining_vacation_days < 0:
                raise UserError(_('أيام الإجازة المتبقية لا يمكن أن تكون سالبة.'))

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id
            self.job_id = self.employee_id.job_id

    # دالة لطباعة التقرير
    def print_vacation_settlement_report(self):
        self.ensure_one()
        return self.env.ref('hr_vacation_settlement.action_report_vacation_settlement').report_action(self)


class HrVacationAdvance(models.Model):
    _name = 'hr.vacation.advance'
    _description = 'سلف الإجازة'

    name = fields.Char(string='الوصف', required=True)
    date = fields.Date(string='التاريخ', default=fields.Date.today)
    amount = fields.Monetary(
        string='المبلغ',
        currency_field='currency_id',
        required=True
    )
    currency_id = fields.Many2one(
        'res.currency', string='العملة',
        related='settlement_id.currency_id', store=True
    )
    settlement_id = fields.Many2one(
        'hr.vacation.settlement',
        string='تصفية الإجازة',
        ondelete='cascade'
    )
    notes = fields.Text(string='ملاحظات')

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise UserError(_('يجب أن يكون مبلغ السلف أكبر من الصفر.'))