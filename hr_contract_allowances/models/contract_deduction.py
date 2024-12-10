# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError, ValidationError


class ContractDeduction(models.Model):
    _name = 'contract.deduction'
    _description = "Contract Deduction"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Deduction Name", default="/", readonly=True)
    date = fields.Date(string="Date", default=fields.Date.today())
    requseter_id = fields.Many2one('res.users', string="Requester", default=lambda self: self.env.user, readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    department_id = fields.Many2one(related='employee_id.department_id', string="Department", readonly=True)
    deduction_lines = fields.One2many('contract.deduction.line', 'deduction_id', string="Deductions Line", index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
    ], string="State", default='draft', copy=False)
    deduction_amount = fields.Float(string="Deduction Amount", required=True, tracking=True)
    total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_deduction_amount')
    balance_amount = fields.Float(string="Balance Amount", compute='_compute_deduction_amount')
    total_paid_amount = fields.Float(string="Total Paid Amount", compute='_compute_deduction_amount')
    installment_type = fields.Selection([
        ('installment_amount', 'Installment Amount'),
        ('installment_no', 'Installment No.'),
    ], string="Payment Type", default='installment_amount', copy=False)
    installment = fields.Integer(string="No Of Installments", default=1)
    installment_amount = fields.Float(string="Installment Amount")
    payment_date = fields.Date(string="Installment Date", required=True, default=fields.Date.today())
    employee_no = fields.Char('Employee No')
    salary = fields.Float()
    description = fields.Text(string="Description", required=True, copy=False)
    is_setto_draft = fields.Boolean(string="Is Set to Draft", compute="_is_set_to_draft")
    payment_ids = fields.Many2many(comodel_name="account.payment", string="Deduction Cash Payment", copy=False)
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", copy=False)


    #override method to make restict on it
    def unlink(self):
        for data in self:
            if data.state not in ['draft']:
                raise UserError(
                    _('You can delete only draft status records...'),
                )
        return super(ContractDeduction, self).unlink()

    #make register payment button
    def make_cash_register_payment(self):
        return {
            'name': _('Contract Cash Register Payment'),
            'res_model': 'cash.deduction.register.payment',
            'view_mode': 'form',
            'context': {
                'active_model': 'contract.deduction',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    #if any status is pending than allow to reset to draft true
    def _is_set_to_draft(self):
        for data in self:
            if data.state == 'approve' and all(line.status == 'pending' for line in data.deduction_lines):
                data.is_setto_draft = True
            else:
                data.is_setto_draft = False

    def approve_deduction(self):
        if not self.deduction_lines:
            raise UserError(_("Please compute installments before Approval .....!"))
        self.state="approve"

    #when click on draft button
    def action_draft(self):
        self.state = 'draft'

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """it get the department of employee it have"""
        for emp in self:
            emp.department_id = emp.employee_id.department_id.id if emp.employee_id.department_id else False
            emp.employee_no = emp.employee_id.employee_number
            if emp.sudo().employee_id.contract_id:
                emp.salary = emp.sudo().employee_id.contract_id.wage

    def _compute_deduction_amount(self):
        """
        it computes total amount and total paid amount ,balance amount fields
        """
        total_paid = 0.0
        for deduction in self:
            for line in deduction.deduction_lines:
                if line.status == 'done':
                    total_paid += line.amount
            balance_amount = deduction.deduction_amount - total_paid
            self.total_amount = deduction.deduction_amount
            self.balance_amount = balance_amount
            self.total_paid_amount = total_paid



    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('contract.deduction.seq')
        res = super(ContractDeduction, self).create(values)
        return res

    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for deduction in self:
            deduction.deduction_lines.unlink()
            amount = 0.0
            installment = 1
            TotalLastAmount = 0.0
            date_start = datetime.strptime(str(deduction.payment_date), '%Y-%m-%d')
            if deduction.installment_type == 'installment_no':
                amount = deduction.deduction_amount / deduction.installment
                installment = deduction.installment
            else:
                amount = deduction.installment_amount
                installment = deduction.deduction_amount / deduction.installment_amount
            if installment == len(self.deduction_lines):
                raise except_orm('Error!', 'Line Already Filled')
            else:
                for i in range(1, int(installment) + 1):
                    self.env['contract.deduction.line'].create({
                        'date': date_start,
                        'amount': amount,
                        'employee_id': deduction.employee_id.id,
                        'deduction_id': deduction.id,
                        'installment_type': deduction.installment_type,
                        'description': str(deduction.description) + '-' + str(date_start)})
                    date_start = date_start + relativedelta(months=1)
            # Last Payment Amonuts CA
            for line in deduction.deduction_lines:
                TotalLastAmount += line.amount
            if (deduction.deduction_amount - TotalLastAmount) > 0:
                self.env['contract.deduction.line'].create({
                    'date': date_start,
                    'amount': deduction.deduction_amount - TotalLastAmount,
                    'employee_id': deduction.employee_id.id,
                    'deduction_id': deduction.id,
                    'installment_type': deduction.installment_type,
                    'description': str(deduction.description) + '-' + str(date_start)})
        return True


class ContractDeductionLine(models.Model):
    _name = 'contract.deduction.line'
    _description = "Installment Line"
    _inherit = ['mail.thread', 'mail.activity.mixin']    
    _rec_name = 'description'

    date = fields.Date(string="Payment Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount", required=True)
    deduction_id = fields.Many2one('contract.deduction', string="Deduction Ref.")
    status = fields.Selection([('pending', 'Pending'), ('done', 'Done'), ('hold', 'Hold')], string="Status",
                              default="pending")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
    description = fields.Text(string="Description")
    installment_type = fields.Selection([
        ('installment_amount', 'Installment Amount'),
        ('installment_no', 'Installment No.'),
    ], string="Payment Type", copy=False)


