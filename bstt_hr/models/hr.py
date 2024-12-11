#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import datetime
from datetime import date
from dateutil import relativedelta
import re
from odoo.exceptions import ValidationError
from stdnum import iban


class Employee(models.Model):
    _inherit = 'hr.employee'

    emp_type = fields.Selection([
        ('national', 'مواطن'),
        ('displaced_tribes', 'قبائل نازحة'),
        ('citizen_son', 'ابن مواطنة'),
        ('foreign', 'مقيم'),
        ('citizen_wife', 'زوجة مواطن'),
        ('citizen_husband', 'زوج مواطنة'),
    ], string='النوع', index=True, tracking=True)

    foreign_name = fields.Char(string="الاسم باللغة الانجليزية", copy=False, tracking=True)
    sponsor = fields.Char(string="الكفيل", copy=False)
    employee_no = fields.Char(string='الرقم الوظيفي')
    iqama_job = fields.Char(string='المهنة بالإقامة', groups="hr.group_hr_user")
    manager_phone = fields.Char(string='رقم صاحب العمل', groups="hr.group_hr_user")
    age = fields.Integer(string='العمر', compute='_compute_employee_age', groups="hr.group_hr_user")
    identification_id = fields.Char(string='رقم الهوية/الاقامة', groups="hr.group_hr_user", tracking=True)
    iqama_expiry_date_hijri = fields.Char(string='تاريخ انتهاء الإقامة بالهجري')

    id_start_date = fields.Date(
        string='تاريخ الاصدار',
        help='Start date of Identification ID')
    id_expiry_date = fields.Date(
        string='تاريخ الانتهاء',
        help='Expiry date of Identification ID')
    id_attachment_id = fields.Many2many(
        'ir.attachment', 'id_attachment_rel',
        'id_ref', 'attach_ref',
        string="المرفق",
        help='You can attach the copy of your Id')
    passport_expiry_date = fields.Date(
        string='تاريخ الانتهاء',
        help='Expiry date of Passport ID')
    passport_start_date = fields.Date(
        string='تاريخ الاصدار',
        help='ٍStart date of Passport ID')
    passport_attachment_id = fields.Many2many(
        'ir.attachment',
        'passport_attachment_rel',
        'passport_ref', 'attach_ref1',
        string="المرفق",
        help='You can attach the copy of Passport')

    fam_ids = fields.One2many(
        'hr.employee.family', 'employee_id',
        string='بيانات العائلة', help='Family Information')
    ins_fam_ids = fields.One2many('hr.employee.family',related='fam_ids',string='بيانات التأمينات  العائلية', store_true=True, readonly=False)
    certificate_id = fields.Many2one('hr.certificates', string='مستوى الشهادة')
    # bank_account_id = fields.Many2one(
    #     'res.partner.bank', 'Bank Account Number',
    #     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    #     groups="hr.group_hr_user",
    #     tracking=True,
    #     help='Employee bank salary account')
    start_work_request_count = fields.Integer(compute="_start_work_request_count")

    bank_account_no = fields.Char(string="رقم حساب البنك")
    bank_id = bank_id = fields.Many2one('res.bank', string="اسم البنك")
    address = fields.Char(string="العنوان")

    """Start Insurance fields"""
    iqama = fields.Char(string="الاقامة")
    iqama_duration = fields.Integer(string="المدة")
    medical_insurance_type_id = fields.Many2one("hr.medical.insurance.type", string="فئة التأمين الطبي",copy=False,tracking=True)
    medical_insurance_value = fields.Float(string="قيمة التأمين", copy=False, tracking=True)
    medical_insurance_duration = fields.Integer(string="مدة التأمين", copy=False, tracking=True)
    medical_insurance_expire_date = fields.Date(string="تاريخ انتهاء التأمين", copy=False, tracking=True)
    medical_insurance_company = fields.Char(string="شركة التأمين", copy=False, tracking=True)
    medical_insurance_life_partner = fields.Float(string="قيمة التأمين للزوجـ/ـة", copy=False, tracking=True)
    medical_insurance_son1 = fields.Float(string="قيمة التأمين للطفل1", copy=False, tracking=True)
    medical_insurance_son2 = fields.Float(string="قيمة التأمين للطفل2", copy=False, tracking=True)
    medical_insurance_son3 = fields.Float(string="قيمة التأمين للطفل3", copy=False, tracking=True)
    medical_insurance_son4 = fields.Float(string="قيمة التأمين للطفل4", copy=False, tracking=True)
    medical_insurance_son5 = fields.Float(string="قيمة التأمين للطفل5", copy=False, tracking=True)
    medical_insurance_son6 = fields.Float(string="قيمة التأمين للطفل6", copy=False, tracking=True)
    medical_insurance_son7 = fields.Float(string="قيمة التأمين للطفل7", copy=False, tracking=True)
    medical_insurance_son8 = fields.Float(string="قيمة التأمين للطفل8", copy=False, tracking=True)
    medical_insurance_son9 = fields.Float(string="قيمة التأمين للطفل9", copy=False, tracking=True)
    medical_insurance_son10 = fields.Float(string="قيمة التأمين للطفل10", copy=False, tracking=True)
    """End Insurance fields"""

    @api.model
    def create(self, vals):
        emp = super(Employee, self).create(vals)
        if vals.get('bank_account_no', False) or vals.get('bank_id', False) or vals.get('address', False):
            partner = self.env['res.partner'].create(
                {'name': emp.name,
                 'street': emp.address or False,
                 })
            emp.address_home_id = partner.id
            if emp.address_home_id and 'bank_account_no' in vals:
                res_partner_bank = self.env['res.partner.bank'].search([('acc_number', '=', vals['bank_account_no'])],
                                                                       limit=1)
                if res_partner_bank.partner_id.id and res_partner_bank.partner_id.id != emp.address_home_id.id:
                    raise UserError(_("يجب ان يكون رقم الحساب البنكي فريد. الرقم الحساب البنكي مسجل باسم %s",
                                      res_partner_bank.partner_id.name))
                elif res_partner_bank.partner_id.id == emp.address_home_id.id:
                    emp.bank_account_id = res_partner_bank.id
                else:
                    emp.bank_account_id = self.env['res.partner.bank'].create({
                        'acc_number': emp.bank_account_no,
                        'bank_id': vals.get('bank_id', False),
                        'company_id': self.env.company.id,
                        # 'currency_id': self.currency_id.id,
                        'partner_id': emp.address_home_id.id,
                    }).id
        return emp

    def write(self, vals):
        if vals.get('bank_account_no', False) or vals.get('bank_id', False) or vals.get('address', False):
            for rec in self:
                if not rec.address_home_id:
                    partner = self.env['res.partner'].create(
                        {'name':  rec.name or vals.get('name', False),
                         'street': vals.get('address', False),
                         })
                    rec.address_home_id = partner.id

                if rec.address_home_id and vals.get('address', False):
                    rec.address_home_id.street = vals.get('address', False)

                if rec.address_home_id and 'bank_account_no' in vals:
                    res_partner_bank = self.env['res.partner.bank'].search([('acc_number', '=', vals['bank_account_no'])], limit=1)
                    if res_partner_bank.partner_id.id and res_partner_bank.partner_id.id != rec.address_home_id.id:
                        raise UserError(_("يجب ان يكون رقم الحساب البنكي فريد. الرقم الحساب البنكي مسجل باسم %s", res_partner_bank.partner_id.name))
                    elif res_partner_bank.partner_id.id == rec.address_home_id.id:
                        rec.bank_account_id = res_partner_bank.id
                    else:
                        rec.bank_account_id = self.env['res.partner.bank'].create({
                            'acc_number': vals.get('bank_account_no', False),
                            'bank_id': vals.get('bank_id', False),
                            'company_id': self.env.company.id,
                            # 'currency_id': self.currency_id.id,
                            'partner_id': rec.address_home_id.id,
                        }).id
        return super().write(vals)

    @api.onchange('identification_id')
    def _onchange_identification_id(self):
        if self.identification_id:
            self.identification_id = re.sub('[^0-9]', '', self.identification_id)
            if len(str(self.identification_id)) != 10:
                raise ValidationError(_("رقم الهوية/الاقامة يجب ان يكون 10 أرقام"))

    def _start_work_request_count(self):
        for employee in self:
            req = self.env['hr.employee.start.work'].sudo().search([('employee_id', '=', employee.id)])
            employee.start_work_request_count = len(req)

    @api.depends('birthday')
    def _compute_employee_age(self):
        age = False
        if self.birthday:
            dob = self.birthday
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        self.age = age

    def action_create_start_work(self):
        """Create the Start Work.
        """
        employee_start_work_count = self.env['hr.employee.start.work'].search_count([
                ('employee_id', '=', self.id), ('state', 'not in', ['approve', 'refuse', 'cancel'])])
        if employee_start_work_count > 0:
            raise UserError(_("لايمكن انشاء طلب مباشرة مع وجود طلب مباشرة تحت الاجراء"))

        action = {
            'name': _('Start Work'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.start.work',
            'context': {"default_employee_id": self.id,},
            'view_mode': 'form',
            'views': [[self.env.ref('bstt_hr.hr_start_work_form_view').id, 'form']],
        }
        return action

    def open_start_work_requests(self):
        self.ensure_one()
        req = self.env['hr.employee.start.work'].sudo().search([('employee_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'طلبات مباشرة العمل',
            'view_mode': 'tree,form',
            'res_model': 'hr.employee.start.work',
            'domain': [('id', 'in', req.ids)]
        }

    def _format_iban(self, bank_account_no):
        '''
        This function removes all characters from given 'string' that isn't a alpha numeric and converts it to upper case, checks checksums and groups by 4
        '''
        res = ''
        if bank_account_no:
            # _logger = logging.getLogger(__name__)
            # _logger.dbug('FGF bank_account_no %s' % (bank_account_no))
            try:
                a = iban.validate(bank_account_no)
            except:
                raise ValidationError(_('%s is not a valid IBAN.') % (bank_account_no))
            res = iban.format(a)
        return res

    @api.onchange('bank_account_no')
    def onchange_acc_id(self):
        result = {}
        if self.bank_account_no:
            result['bank_account_no'] = self._format_iban(self.bank_account_no)

        return {'value': result}

    # @api.onchange('job_id')
    # def onchange_job_id(self):
    #     if self.job_id:
    #         self.job_title = self.job_id.name


class EmployeeRelationInfo(models.Model):
    """Table for keep employee family information"""
    _name = 'hr.employee.relation'

    name = fields.Char(string="Relationship",
                       help="Relationship with thw employee")


class HRCertificates(models.Model):
    _name = 'hr.certificates'

    name = fields.Char(string="الاسم")


class HrEmployeeFamilyInfo(models.Model):
    """Table for keep employee family information"""
    _name = 'hr.employee.family'
    _description = 'HR Employee Family'

    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  help='Select corresponding Employee',
                                  invisible=1)
    relation_id = fields.Many2one('hr.employee.relation', string="نوع الصلة", help="Relationship with the employee")
    member_name = fields.Char(string='الاسم')
    member_contact = fields.Char(string='رقم الجوال')
    member_identification_id = fields.Char(string='رقم الهوية/الاقامة')
    birth_date = fields.Date(string="تاريخ الميلاد", tracking=True)
    insurance_amount = fields.Float(string='القيمة')
