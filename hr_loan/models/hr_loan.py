# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrLoanType(models.Model):
    _name = 'hr.loan.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Type"

    name = fields.Char()
    rule_code = fields.Char(string="كود قاعدة المرتبات")
    rule_structure_id = fields.Many2one('hr.payroll.structure', string='هيكل المرتب')
    default_account = fields.Many2one('account.account',string="Account name")

    credit_account_id = fields.Many2one('account.account', string="حساب المدين")
    debit_account_id = fields.Many2one('account.account', string="حساب الدائن")
    journal_id = fields.Many2one('account.journal', string='اليومية')

    def write(self, vals):
        res = super(HrLoanType, self).write(vals)
        if vals.get('rule_code', False) or vals.get('name', False) or vals.get('rule_structure_id', False):
            is_rule_exite = self.env['hr.salary.rule'].search(
                [('code', '=', self.rule_code), ('name', '=', self.name), ('struct_id', '=', self.rule_structure_id.id)], limit=1)
            if not is_rule_exite:
                amount_python_compute = 'result = inputs.' + self.rule_code + ' and - (inputs.' + self.rule_code + '.amount)'
                condition_python = 'result = inputs.' + self.rule_code + ' and (inputs.' + self.rule_code + '.amount)'

                deduct_rules_sequence = self.env['hr.salary.rule'].search(
                    [('category_id', '=', self.env.ref('hr_payroll.DED').id)], order="sequence desc", limit=1).sequence

                input_type = self.env['hr.payslip.input.type'].create({
                    'code': self.rule_code,
                    'name': self.name,
                })

                obj = self.env['hr.salary.rule'].create({
                    'name': self.name,
                    'sequence': deduct_rules_sequence,
                    'category_id': self.env.ref('hr_payroll.DED').id,
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
        res = super(HrLoanType, self).create(values)
        is_rule_exite = self.env['hr.salary.rule'].search(
            [('code', '=', res.rule_code), ('name', '=', res.name),
             ('struct_id', '=', res.rule_structure_id.id)], limit=1)
        if not is_rule_exite:
            amount_python_compute = 'result = inputs.'+res.rule_code+' and - (inputs.'+res.rule_code+'.amount)'
            condition_python = 'result = inputs.'+res.rule_code+' and (inputs.'+res.rule_code+'.amount)'

            deduct_rules_sequence = self.env['hr.salary.rule'].search([('category_id', '=', self.env.ref('hr_payroll.DED').id)], order="sequence desc", limit=1).sequence

            input_type = self.env['hr.payslip.input.type'].create({
                'code': res.rule_code,
                'name': res.name,
            })

            obj = self.env['hr.salary.rule'].create({
                        'name': res.name,
                        'sequence': deduct_rules_sequence,
                        'category_id': self.env.ref('hr_payroll.DED').id,
                        'condition_select': "python",
                        'condition_python': condition_python,
                        'amount_select': "code",
                        'amount_python_compute': amount_python_compute,
                        'code': res.rule_code,
                        'struct_id': res.rule_structure_id.id
            })
        return res


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    @api.model
    def default_get(self, field_list):
        result = super(HrLoan, self).default_get(field_list)
        if result.get('user_id'):
            ts_user_id = result['user_id']
        else:
            ts_user_id = self.env.context.get('user_id', self.env.user.id)
        result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
        return result

    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.paid:
                    total_paid += line.amount
            balance_amount = loan.loan_amount - total_paid
            loan.total_amount = loan.loan_amount
            loan.balance_amount = balance_amount
            loan.total_paid_amount = total_paid

    name = fields.Char(string="Loan Name", default="/", readonly=True, help="Name of the loan")
    reason = fields.Char(string="Reason")
    is_responsible_approve = fields.Boolean(compute="is_responsible_approve_chk", default=False)
    responsible_approve_id = fields.Many2one('res.users', string='Responsible for Approve', required=True,
                                 domain=lambda self: [('groups_id', '=', self.env.ref('hr_loan.group_loan_request_approver').id)])
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, help="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee",  domain=[('contract_id', '!=', False)])
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Department", help="Employee")
    installment = fields.Integer(string="No Of Installments", default=1, help="Number of installments")
    payment_date = fields.Date(string="Payment Start Date", required=True, default=fields.Date.today(), help="Date of "
                                                                                                             "the "
                                                                                                             "paymemt")
    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position",
                                   help="Job position")
    loan_amount = fields.Float(string="Loan Amount", required=True, help="Loan amount")
    total_amount = fields.Float(string="Total Amount", store=True, readonly=True, compute='_compute_loan_amount',
                                help="Total loan amount")
    balance_amount = fields.Float(string="Balance Amount", store=True, compute='_compute_loan_amount',
                                  help="Balance amount")
    total_paid_amount = fields.Float(string="Total Paid Amount", store=True, compute='_compute_loan_amount',
                                     help="Total paid amount")
    loan_type_id = fields.Many2one('hr.loan.type', string="Loan-Advance Type")

    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)


    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )


    @api.onchange('loan_lines')
    def onchange_total_paid_amount(self):
        total = 0.0
        for line in self.loan_lines:
            total += line.amount
        print("total", total)
        if total > self.total_amount:
            raise ValidationError(_('Total amount must be greater than or equal to total paid amount'))

    @api.model
    def create(self, values):
        # loan_count = self.env['hr.loan'].search_count(
        #     [('employee_id', '=', values['employee_id']), ('state', '=', 'approve'),
        #      ('balance_amount', '!=', 0)])
        # if loan_count:
        #     raise ValidationError(_("The employee has already a pending installment"))
        # else:
        values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
        res = super(HrLoan, self).create(values)
        return res

    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for loan in self:
            loan.loan_lines.unlink()
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            amount = loan.loan_amount / loan.installment
            for i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id,

                })
                date_start = date_start + relativedelta(months=1)
            loan._compute_loan_amount()
        return True

    def action_refuse(self):
        moves = self.mapped('move_id')
        moves.filtered(lambda x: x.state == 'posted').button_cancel()
        # moves.unlink()
        return self.write({'state': 'refuse'})

    def action_submit(self):
        self.write({'state': 'waiting_approval_1'})
        self.activity_schedule('mail.mail_activity_data_todo', user_id=self.responsible_approve_id.id)

    def action_cancel(self):
        moves = self.mapped('move_id')
        moves.filtered(lambda x: x.state == 'posted').button_cancel()
        # moves.unlink()
        self.write({'state': 'cancel'})

    def action_reset_to_draft(self):
        moves = self.mapped('move_id')
        moves.filtered(lambda x: x.state == 'posted').button_cancel()
        # moves.unlink()
        self.write({'state': 'draft'})

    def action_approve(self):
        for data in self:
            if not data.loan_lines:
                raise ValidationError(_("Please Compute installment"))
            else:
                self.action_create_journal_entry()
                # self.action_create_payment()

                self.write({'state': 'approve'})

    def is_responsible_approve_chk(self):
        for rec in self:
            rec.is_responsible_approve = False
            if self.env.user.id == rec.responsible_approve_id.id and self.env.user.has_group('hr_loan.group_loan_request_approver'):
                rec.is_responsible_approve = True

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

    # def action_create_journal_entry(self):
    #     config_parameter = self.env['ir.config_parameter'].sudo()
    #     debit_account_id = config_parameter.get_param("hr_loan.debit_account_id", False)
    #     credit_account_id = config_parameter.get_param("hr_loan.credit_account_id", False)
    #     journal = config_parameter.get_param("hr_loan.journal_id", False)
    #     if not debit_account_id :
    #         raise ValidationError(_("Please add debit account"))
    #     if not credit_account_id :
    #         raise ValidationError(_("Please add credit account"))
    #     if not journal :
    #         raise ValidationError(_("Please add journal"))
    #     move_lines = []
    #
    #     # add total debit journal item
    #     print(self.employee_id.address_home_id, "self.employee_id.user_partner_id")
    #     move_lines.append([0, 0, self._prepare_journal_entry_line(eval(debit_account_id),partner=self.employee_id.address_home_id.id, debit=self.total_amount)])
    #     # add total credit journal item
    #     move_lines.append([0, 0, self._prepare_journal_entry_line(eval(credit_account_id), credit=self.total_amount)])
    #     vals = {
    #         'date': self.date,
    #         'journal_id': eval(journal),
    #         'line_ids': move_lines
    #     }
    #     print(vals)
    #     self.env['account.move'].create(vals)
    #     return True

    def action_create_journal_entry(self):
        debit_account_id = self.loan_type_id.debit_account_id
        credit_account_id = self.loan_type_id.credit_account_id
        journal = self.loan_type_id.journal_id
        if not debit_account_id :
            raise ValidationError(_("Please add debit account"))
        if not credit_account_id :
            raise ValidationError(_("Please add credit account"))
        if not journal :
            raise ValidationError(_("Please add journal"))
        if not self.employee_id.address_home_id.id :
            partner = self.env['res.partner'].create(
                    {'name': self.employee_id.name,
                     'street': self.employee_id.address or False,
                     })
            self.employee_id.address_home_id = partner.id
        move_lines = []

        # add total debit journal item
        move_lines.append([0, 0, self._prepare_journal_entry_line(debit_account_id.id,partner=self.employee_id.address_home_id.id, debit=self.total_amount)])
        # add total credit journal item
        move_lines.append([0, 0, self._prepare_journal_entry_line(credit_account_id.id, credit=self.total_amount)])
        vals = {
            'date': self.date,
            'journal_id': journal.id,
            'line_ids': move_lines
        }
        # print(vals)
        move = self.env['account.move'].create(vals)
        self.move_id = move.id
        return True

    def action_create_payment(self):
        payment_obj = self.env['account.payment']
        payment_obj.create({
            'payment_type':'outbound',
            'partner_type':'supplier',
            'partner_id':self.employee_id.address_home_id.id,
            'amount':self.loan_amount,
            'loan_type_id':self.loan_type_id.id,
            'is_loan': True,
            'destination_account_id':self.loan_type_id.default_account.id,

        })

    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(
                    'You cannot delete a loan which is not in draft or cancelled state')
        return super(HrLoan, self).unlink()


class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True, help="Date of the payment")
    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
    amount = fields.Float(string="Amount", required=True, help="Amount")
    paid = fields.Boolean(string="Paid", help="Paid")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.", help="Loan")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")


    def unlink(self):
        for line in self:
            if line.paid:
                raise ValidationError(_('Can not delete paid line'))
        return super(InstallmentLine, self).unlink()


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', self.id)])

    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')
