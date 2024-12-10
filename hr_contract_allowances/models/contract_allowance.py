# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError, ValidationError


class ContractAllowance(models.Model):
    _name = 'contract.allowance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Contract Allowance"

    name = fields.Char(string="Allowance Name", default="/", readonly=True)
    date = fields.Date(string="Date", default=fields.Date.today())
    requseter_id = fields.Many2one('res.users', string="Requester", default=lambda self: self.env.user, readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    department_id = fields.Many2one(related='employee_id.department_id', string="Department", readonly=True)
    allowance_lines = fields.One2many('contract.allowance.line', 'allowance_id', string="Allowance Line", index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
    ], string="State", default='draft', copy=False)
    allowance_amount = fields.Float(string="Allowance Amount", required=True, tracking=True)
    total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_allowance_amount')
    balance_amount = fields.Float(string="Balance Amount", compute='_compute_allowance_amount')
    total_paid_amount = fields.Float(string="Total Paid Amount", compute='_compute_allowance_amount')
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

    #override method to make restict on it
    def unlink(self):
        for data in self:
            if data.state not in ['draft']:
                raise UserError(
                    _('You can delete only draft status records...'),
                )
        return super(ContractAllowance, self).unlink()
    #if any status is pending than allow to reset to draft true
    def _is_set_to_draft(self):
        for data in self:
            if data.state == 'approve' and all(line.status == 'pending' for line in data.allowance_lines):
                data.is_setto_draft = True
            else:
                data.is_setto_draft = False

    #when click on draft button
    def action_draft(self):
        self.state = 'draft'

    def approve_allowance(self):
        if not self.allowance_lines:
            raise UserError(_("Please compute installments before Approval .....!"))
        self.state="approve"

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """it get the department of employee it have"""
        for emp in self:
            emp.department_id = emp.employee_id.department_id.id if emp.employee_id.department_id else False
            emp.employee_no = emp.employee_id.employee_number
            if emp.sudo().employee_id.contract_id:
                emp.salary = emp.sudo().employee_id.contract_id.wage

    def _compute_allowance_amount(self):
        """
        it computes total amount and total paid amount ,balance amount fields
        """
        total_paid = 0.0
        for allowance in self:
            for line in allowance.allowance_lines:
                if line.status == 'done':
                    total_paid += line.amount
            balance_amount = allowance.allowance_amount - total_paid
            self.total_amount = allowance.allowance_amount
            self.balance_amount = balance_amount
            self.total_paid_amount = total_paid



    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('contract.allowance.seq')
        res = super(ContractAllowance, self).create(values)
        return res

    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for allowance in self:
            allowance.allowance_lines.unlink()
            amount = 0.0
            installment = 1
            TotalLastAmount = 0.0
            date_start = datetime.strptime(str(allowance.payment_date), '%Y-%m-%d')
            if allowance.installment_type == 'installment_no':
                amount = allowance.allowance_amount / allowance.installment
                installment = allowance.installment
            else:
                amount = allowance.installment_amount
                installment = allowance.allowance_amount / allowance.installment_amount
            if installment == len(self.allowance_lines):
                raise except_orm('Error!', 'Line Already Filled')
            else:
                for i in range(1, int(installment) + 1):
                    self.env['contract.allowance.line'].create({
                        'date': date_start,
                        'amount': amount,
                        'employee_id': allowance.employee_id.id,
                        'allowance_id': allowance.id,
                        'installment_type': allowance.installment_type,
                        'description': str(allowance.description) + '-' + str(date_start)})
                    date_start = date_start + relativedelta(months=1)
            # Last Payment Amonuts CA
            for line in allowance.allowance_lines:
                TotalLastAmount += line.amount
            if (allowance.allowance_amount - TotalLastAmount) > 0:
                self.env['contract.allowance.line'].create({
                    'date': date_start,
                    'amount': allowance.allowance_amount - TotalLastAmount,
                    'employee_id': allowance.employee_id.id,
                    'allowance_id': allowance.id,
                    'installment_type': allowance.installment_type,
                    'description': str(allowance.description) + '-' + str(date_start)})
        return True


class ContractAllowanceLine(models.Model):
    _name = 'contract.allowance.line'
    _description = "Installment Line"
    _rec_name = 'description'

    date = fields.Date(string="Payment Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount", required=True)
    allowance_id = fields.Many2one('contract.allowance', string="Allowance Ref.")
    status = fields.Selection([('pending', 'Pending'), ('done', 'Done'), ('hold', 'Hold')], string="Status",
                              default="pending")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
    description = fields.Text(string="Description")
    installment_type = fields.Selection([
        ('installment_amount', 'Installment Amount'),
        ('installment_no', 'Installment No.'),
    ], string="Payment Type", copy=False)


