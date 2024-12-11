# -*- coding: utf-8 -*-

from dateutil import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEndOfService(models.Model):
    _name = 'hr.end.service'
    _description = 'Hr End Of Service'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Number", copy=False, index=True, tracking=True, readonly=True, default=_("New"))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True, copy=False,
                                  domain=[('contract_id', '!=', False)])
    join_date = fields.Date(related='contract_id.date_start', string="Join Date", tracking=True, copy=False, store=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', store=True)
    date = fields.Date(string="Date", tracking=True, index=True, copy=False, required=True)
    reason = fields.Selection([
        ('contract_end', 'اتفاق العامل وصاحب العمل على إنهاء العقد'),
        ('contract_end_2', 'ترك العامل العمل نتيجة لقوة قاهرة'),
        ('contract_end_3', 'إنهاء العاملة لعقد العمل خلال ستة أشهر من عقد الزواج أو خلال ثلاثة أشهر من الوضع'),
        ('contract_end_4', 'ترك العامل العمل لأحد الحالات الواردة في المادة (81)'),
        ('contract_end_5', 'فسخ العقد من قبل صاحب العمل ولم يكن وفق المادة (80)'),
        ('termination', 'فسخ العقد من قبل صاحب العمل لأحد الحالات الواردة في المادة (80)'),
        ('termination_2', 'ترك العامل العمل دون تقديم استقالة لغير الحالات الواردة في المادة (81)'),
        ('resignation', 'استقالة العامل'),
    ], string="Reason", index=True, required=True, tracking=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', index=True, required=True, tracking=True, copy=False,
                                 default=lambda self: self.env.company.id)
    department_id = fields.Many2one(related='employee_id.department_id', string='Department', tracking=True, store=True,
                                    copy=False)
    manager_id = fields.Many2one(related='employee_id.parent_id', string='Manager', tracking=True, store=True,
                                 copy=False)
    job_id = fields.Many2one(related='employee_id.job_id', string='Job Position', store=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'IN Progress'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], string='State', index=True, readonly=True, default='draft', copy=False,
        tracking=True)

    total_service = fields.Char(string="Total Service", compute='_compute_total_end_service', stote=True, readonly=True)
    total_service_year = fields.Float(string="Total Service Years", compute='_compute_total_end_service', stote=True,
                                      readonly=True)
    service_year = fields.Integer(string="Total Service Years", compute='_compute_total_end_service', stote=True,
                                  readonly=True)
    service_month = fields.Integer(string="Total Service Months", compute='_compute_total_end_service', stote=True,
                                   readonly=True)
    service_day = fields.Integer(string="Total Service Days", compute='_compute_total_end_service', stote=True,
                                 readonly=True)
    note = fields.Text(string="Notes", copy=False)
    reject_reason = fields.Text(string="Reject Reason", copy=False)
    eos_total = fields.Float(string="EOS Total", compute="_eos_total",store=True)
    paid = fields.Boolean(string="Paid", help="Paid", default=False)
    eos_setting_id = fields.Many2one('hr.end.service.setting', string="Hr End Of Service Setting")
    eos_setting_type = fields.Selection(related="eos_setting_id.type", string="Hr End Of Service Setting Type")
    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)

    @api.depends('service_day','service_year','reason')
    def _eos_total(self):
        for eos in self:
            wage = eos.employee_id.contract_id.wage
            eos_total = 0.0
            if eos.total_service_year <= 5 or eos.total_service_year > 5:
                eos_total += (wage / 2) * (eos.total_service_year if eos.total_service_year <= 5 else 5)
            if eos.total_service_year > 5:
                eos_total += wage * (eos.total_service_year - 5)

            if eos.reason == 'resignation':
                if eos.total_service_year < 2:
                    eos.eos_total = 0.0
                if 2 <= eos.total_service_year < 5:
                    eos.eos_total = (eos_total / 3)
                if 5 <= eos.total_service_year < 10:
                    eos.eos_total = (eos_total * 2/3)
                if eos.total_service_year >= 10:
                    eos.eos_total = eos_total

            if eos.reason in ('termination','termination_2'):
                eos.eos_total = 0.0

            if eos.reason in ('contract_end','contract_end_2','contract_end_3','contract_end_4','contract_end_5'):
                eos.eos_total = eos_total

    @api.constrains('date')
    def _check_date(self):
        for end_service in self:
            if end_service.join_date and end_service.join_date > end_service.date:
                raise ValidationError(_('Date must be greater than or equal to join date'))

    @api.constrains('employee_id')
    def _check_employee_id(self):
        for end_service in self:
            if self.search([("id", "!=", end_service.id), ("state", "!=", "rejected"),
                            ("employee_id", "=", end_service.employee_id.id)]):
                raise ValidationError(_("This employee already have end of service"))

    @api.depends("join_date", "date")
    def _compute_total_end_service(self):
        for end_service in self:
            join_date = end_service.join_date
            date = end_service.date
            diff = relativedelta.relativedelta(date, join_date)
            years = diff.years
            months = diff.months
            days = diff.days
            total_service = ""
            if years != 0:
                total_service += str(years) + " Years "

            if months != 0:
                total_service += str(months) + " Months "
            if days != 0:
                total_service += str(days + 1) + " Days "
                days=(end_service.date-end_service.join_date).days
            end_service.service_year = years
            end_service.service_month = months
            end_service.service_day = days

            end_service.total_service = total_service
            end_service.total_service_year = float(years + (months / 12))

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.contract_id = self.employee_id.contract_id

    def unlink(self):
        for end_service in self:
            if end_service.state != "draft":
                raise ValidationError(_("Only draft end of service can be delete"))
        return super(HrEndOfService, self).unlink()

    def action_confirm(self):
        for end_service in self:
            if end_service.state != "draft":
                continue
            end_service.write({"state": "in_progress", "name": self.env['ir.sequence'].next_by_code('hr.end.service')})
        return True

    def action_reset_to_draft(self):
        for end_service in self:
            if end_service.state != "rejected":
                continue
            end_service.write({"state": "draft"})
        return True

    def action_reject_reason(self):
        action = self.sudo().env.ref("hr_end_of_service.action_reject_reason_wizard", False)
        result = action.read()[0]
        return result

    def action_open_payslip(self):
        payslip = self.env['hr.payslip'].search([('end_service_id', '=', self.id)], limit=1)
        result = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.payslip',
            'res_id': payslip.id,
        }
        if not payslip:
            result["context"] = {
                "default_employee_id": self.employee_id.id,
                "default_struct_id": self.env.ref("hr_end_of_service.end_of_service_structure").id,
                "default_end_service_id": self.id,
                "default_date_from": self.date.replace(day=1),
                "default_date_to": self.date,
                'contract_id':self.contract_id.id,
            }

        return result

    def action_approve(self):
        for end_service in self:
            if end_service.state != "in_progress":
                continue
            if self.eos_setting_id.type == 'journal':
                self.action_create_journal_entry()
            else:
                payslip = self.env['hr.payslip'].create({
                    'name': 'Payslip',
                    'employee_id': self.employee_id.id,
                    'end_service_id': self.id,
                    'date_from': end_service.date.replace(day=1),
                    'date_to': end_service.date,
                })
                payslip.compute_sheet()
                payslip.write({'struct_id': self.eos_setting_id.rule_structure_id.id})

            end_service.write({"state": "approved"})
        return True

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'draft':
            return self.env.ref('hr_end_of_service.mt_end_of_service_draft')
        elif 'state' in init_values and self.state == 'in_progress':
            return self.env.ref('hr_end_of_service.mt_end_of_service_in_progress')
        elif 'state' in init_values and self.state == 'approved':
            return self.env.ref('hr_end_of_service.mt_end_of_service_approved')
        elif 'state' in init_values and self.state == 'rejected':
            return self.env.ref('hr_end_of_service.mt_end_of_service_rejected')
        return super(HrEndOfService, self)._track_subtype(init_values)

    @api.model
    def _prepare_journal_entry_line(self, account,partner=False, debit=0, credit=0):
        vals = {
            "date_maturity": self.date,
            "debit": debit,
            "credit": credit,
            "partner_id": partner,
            "account_id": account
        }
        return vals
    
    def action_create_journal_entry(self):
        debit_account_id = self.eos_setting_id.debit_account_id
        credit_account_id = self.eos_setting_id.credit_account_id
        journal = self.eos_setting_id.journal_id
        if not debit_account_id :
            raise ValidationError(_("Please add debit account"))
        if not credit_account_id :
            raise ValidationError(_("Please add credit account"))
        if not journal :
            raise ValidationError(_("Please add journal"))
        if not self.employee_id.address_home_id.id :
            raise ValidationError(_("Please add Employee Bank Account No."))
        move_lines = []

        # add total debit journal item
        move_lines.append([0, 0, self._prepare_journal_entry_line(debit_account_id.id,partner=self.employee_id.address_home_id.id, debit=self.eos_total)])
        # add total credit journal item
        move_lines.append([0, 0, self._prepare_journal_entry_line(credit_account_id.id, credit=self.eos_total)])
        vals = {
            'date': self.date,
            'journal_id': journal.id,
            'line_ids': move_lines
        }
        # print(vals)
        move = self.env['account.move'].create(vals)
        self.move_id = move.id
        return True


class HrEndOfServiceSetting(models.Model):
    _name = 'hr.end.service.setting'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hr End Of Service Setting"

    name = fields.Char()
    type = fields.Selection([
        ('journal', 'Journal'),
        ('salary_structure', 'Salary Structure')], string="Type", index=True, required=True, tracking=True, copy=False)

    rule_code = fields.Char(string="كود قاعدة المرتبات")
    rule_structure_id = fields.Many2one('hr.payroll.structure', string='هيكل المرتب')

    credit_account_id = fields.Many2one('account.account', string="حساب المدين")
    debit_account_id = fields.Many2one('account.account', string="حساب الدائن")
    journal_id = fields.Many2one('account.journal', string='اليومية')

    def write(self, vals):
        res = super(HrEndOfServiceSetting, self).write(vals)
        if vals.get('rule_code', False) or vals.get('name', False) or vals.get('rule_structure_id', False):
            is_rule_exite = self.env['hr.salary.rule'].search(
                [('code', '=', self.rule_code), ('name', '=', self.name), ('struct_id', '=', self.rule_structure_id.id)], limit=1)
            if not is_rule_exite:
                amount_python_compute = 'result = inputs.' + self.rule_code + ' and - (inputs.' + self.rule_code + '.amount)'
                condition_python = 'result = inputs.' + self.rule_code + ' and (inputs.' + self.rule_code + '.amount)'

                deduct_rules_sequence = self.env['hr.salary.rule'].search(
                    [('category_id', '=', self.env.ref('hr_payroll.ALW').id)], order="sequence desc", limit=1).sequence

                input_type = self.env['hr.payslip.input.type'].create({
                    'code': self.rule_code,
                    'name': self.name,
                })

                obj = self.env['hr.salary.rule'].create({
                    'name': self.name,
                    'sequence': deduct_rules_sequence,
                    'category_id': self.env.ref('hr_payroll.ALW').id,
                    'condition_select': "python",
                    'condition_python': condition_python,
                    'amount_select': "code",
                    'amount_python_compute': amount_python_compute,
                    'code': self.rule_code,
                    'struct_id': self.rule_structure_id.id
                })
            return res

    @api.model
    def create(self, values):
        res = super(HrEndOfServiceSetting, self).create(values)
        if values.get('rule_code', False) or values.get('rule_structure_id', False):
            is_rule_exite = self.env['hr.salary.rule'].search(
                [('code', '=', res.rule_code), ('name', '=', res.name),
                 ('struct_id', '=', res.rule_structure_id.id)], limit=1)
            if not is_rule_exite:
                amount_python_compute = 'result = inputs.'+res.rule_code+' and - (inputs.'+res.rule_code+'.amount)'
                condition_python = 'result = inputs.'+res.rule_code+' and (inputs.'+res.rule_code+'.amount)'

                deduct_rules_sequence = self.env['hr.salary.rule'].search([('category_id', '=', self.env.ref('hr_payroll.ALW').id)], order="sequence desc", limit=1).sequence

                input_type = self.env['hr.payslip.input.type'].create({
                    'code': res.rule_code,
                    'name': res.name,
                })

                obj = self.env['hr.salary.rule'].create({
                            'name': res.name,
                            'sequence': deduct_rules_sequence,
                            'category_id': self.env.ref('hr_payroll.ALW').id,
                            'condition_select': "python",
                            'condition_python': condition_python,
                            'amount_select': "code",
                            'amount_python_compute': amount_python_compute,
                            'code': res.rule_code,
                            'struct_id': res.rule_structure_id.id
                })
        return res

