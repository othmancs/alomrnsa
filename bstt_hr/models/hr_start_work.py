#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EmployeeStartWork(models.Model):
    _name = 'hr.employee.start.work'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'مباشرة العمل'

    name = fields.Char('وصف طلب المباشرة', required=True)
    guidance = fields.Char('التوجيه')
    employee_id = fields.Many2one('hr.employee', string="الموظف", required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, string="الشركة")
    employee_no = fields.Char(related="employee_id.employee_no", string='الرقم الوظيفي', readonly=True, store=True)
    start_work_date = fields.Date(string='تاريخ المباشرة', required=True)
    start_work_type = fields.Selection([('first', 'باشر الوظيفة لأول مرة / تعيين او نقل'),
                                        ('after_annual_holiday', 'باشر العمل بعد إجازة سنوية'),
                                        ('after_sick_holiday', 'باشر العمل بعد إجازة مرضية'),
                                        ('after_exceptional_holiday', 'باشر العمل بعد إجازة اضطرارية'),
                                        ('after_education', 'باشر العمل بعد دورة تدريبة / دراسية'),
                                        ('after_task', 'باشر العمل بعد انهاء مهمة / تكليف')],
                                       string='نوع المباشرة', required=True, copy=False)
    work_action_type = fields.Selection([('exemption', 'الاعفاء من أي قرار'),
                                        ('draw_attention', 'لفت نظر للموظف'),
                                        ('deduct_from_salary', 'حسم عدد أيام التجاوز من الراتب'),
                                        ('deduct_from_holiday', 'حسم عدد أيام التجاوز من اإلجازة السنوية القادمة')
                                        ],
                                       string='اإلجراءات المتخذة في حال التجاوز', required=True, copy=False)

    job_id = fields.Many2one(related='employee_id.job_id', string='المسمى الوظيفي', store=True, readonly=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='القسم', store=True, readonly=True)
    project_id = fields.Many2one(related='employee_id.work_location_id.project_id', string='المشروع', store=True, readonly=True)
    # wage = fields.Monetary(related='employee_id.contract_id.wage', string='الراتب', store=True, readonly=True)
    is_project_manager = fields.Boolean(compute="is_project_manager_chk", default=False)

    state = fields.Selection([
        ('draft', 'مسودة'),
        ('project_manager', 'مدير المشروع'),
        ('hr_manager', 'مدير الموارد البشرية'),
        ('executive_manager', 'المدير التنفيذي'),
        ('approve', 'مقبول'),
        ('refuse', 'مرفوض'),
        ('cancel', 'ملغي'),
    ], string="State", default='draft', track_visibility='onchange', copy=False)

    def is_project_manager_chk(self):
        for rec in self:
            rec.is_project_manager = False
            if self.env.user.id == rec.project_id.user_id.id or self.env.user.has_group('bstt_hr.group_project_manager_exceptional'):
                rec.is_project_manager = True

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_project_manager(self):
        self.write({'state': 'project_manager'})
        self.activity_schedule('mail.mail_activity_data_todo', user_id=self.project_id.user_id.id)

    def action_hr_manager(self):
        self.write({'state': 'hr_manager'})
        self.activity_feedback(['mail.mail_activity_data_todo'])
        users = self.env['res.users'].search([])
        for user in users:
            if user.has_group('bstt_hr.group_hr_manager_group'):
                # self.add_follower_id(self.id, user.partner_id)
                self.activity_schedule('mail.mail_activity_data_todo', user_id=user.id)

    def action_executive_manager(self):
        self.write({'state': 'executive_manager'})
        self.activity_feedback(['mail.mail_activity_data_todo'])
        users = self.env['res.users'].search([])
        for user in users:
            if user.has_group('bstt_hr.group_executive_manager'):
                # self.add_follower_id(self.id, user.partner_id)
                self.activity_schedule('mail.mail_activity_data_todo', user_id=user.id)

    def action_approve(self):
        self.activity_feedback(['mail.mail_activity_data_todo'])
        self.write({'state': 'approve'})

    @api.model
    def create(self, vals):
        if vals.get('employee_id'):
            employee_count = self.env['hr.employee.start.work'].search_count([
                ('employee_id', '=', vals['employee_id']), ('state', 'not in', ['approve', 'refuse', 'cancel'])])
            if employee_count > 0:
                raise UserError(_("لايمكن انشاء طلب مباشرة مع وجود طلب مباشرة تحت الاجراء"))

        obj = super(EmployeeStartWork, self).create(vals)
        return obj

    # def unlink(self):
    #     if self.filtered('state') == 'approve':
    #         raise UserError(_('لايمكن حذف طلب مباشرة العمل في حالة الموافقة'))
    #     super(EmployeeStartWork, self).unlink()
    #     return True