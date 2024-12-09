# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import models, fields, api, _
from dateutil import relativedelta
from datetime import date,datetime
from odoo.exceptions import UserError


class HrEmployeeEos(models.Model):
    _name = 'hr.employee.eos'
    _inherit = ['mail.thread']
    _description = "End of Service Indemnity (EOS)"

    def _get_currency(self):
        """
            return currency of current user
        """
        user = self.env['res.users'].browse(self.env.uid)
        return user.company_id.currency_id.id

    def _calc_payable_eos(self):
        """
            Calculate the payable eos
        """
        for eos_amt in self:
            # eos_amt.payable_eos = (eos_amt.total_eos + eos_amt.current_month_salary + eos_amt.others + eos_amt.annual_leave_amount+eos_amt.ticket_value + eos_amt.other_allowance - eos_amt.remaining_amount_loan) or 0.0
            eos_amt.payable_eos = (eos_amt.total_eos + eos_amt.annual_leave_amount+eos_amt.ticket_value + eos_amt.other_allowance - eos_amt.others - eos_amt.remaining_amount_loan) or 0.0

    name = fields.Char('Description', size=128, required=True, readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    eos_date = fields.Date('Date', index=True, required=True, readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, default=lambda self: datetime.today().date())
    employee_id = fields.Many2one('hr.employee', "Employee", required=True, readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    date_of_join = fields.Date(related='employee_id.date_of_join', type="date", string="Joining Date", store=True)
    date_of_leave = fields.Date(related='employee_id.date_of_leave', type="date", string="Leaving Date", store=True)
    duration_days = fields.Integer('No of Days', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    duration_months = fields.Integer('No of Months', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    duration_years = fields.Integer('No. of Years', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    type = fields.Selection([('resignation', 'Resignation'), ('termination', 'Termination'), ('death', 'Death')], 'Type', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    calc_year = fields.Float('Total Years', readonly=True, states={'draft': [('readonly', False)]})
    payslip_id = fields.Many2one('hr.payslip', 'Payslip', readonly=True)
    current_month_salary = fields.Float('Salary of Current month', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    others = fields.Float('Others', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    user_id = fields.Many2one('res.users', 'User', required=True, default=lambda self: self.env.uid)
    date_confirm = fields.Date('Confirmation Date', index=True, help="Date of the confirmation of the sheet expense. It's filled when the button Confirm is pressed.")
    date_valid = fields.Date('Validation Date', index=True, help="Date of the acceptation of the sheet eos. It's filled when the button Validate is pressed.", readonly=True)
    date_approve = fields.Date('Approve Date', index=True, help="Date of the Approval of the sheet eos. It's filled when the button Approve is pressed.", readonly=True)
    user_valid = fields.Many2one('res.users', 'Validation by', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, store=True)
    user_approve = fields.Many2one('res.users', 'Approval by', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, store=True)
    note = fields.Text('Note')
    annual_leave_amount = fields.Float('Leave Balance', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', "Department", readonly=True)
    job_id = fields.Many2one('hr.job', 'Job', readonly=True)
    contract_id = fields.Many2one('hr.contract', 'Contract', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, default=lambda self: self.env.user.company_id)
    state = fields.Selection([('draft', 'New'),
                              ('cancelled', 'Refused'),
                              ('confirm', 'Waiting Approval'),
                              ('validate', 'Validated'),
                              ('accepted', 'Approved'),
                              ('done', 'Done')], 'Status', readonly=True, track_visibility='onchange', default='draft',
                             help='When the eos request is created the status is \'Draft\'.\n It is confirmed by the user and request is sent to finance, the status is \'Waiting Confirmation\'.\
        \nIf the finance accepts it, the status is \'Accepted\'.')
    total_eos = fields.Float('Total Award', readonly=True, states={'draft': [('readonly', False)]})
    payable_eos = fields.Float(compute=_calc_payable_eos, string='Total Amount')
    remaining_leave = fields.Float('Remaining Leave')
    ticket_value = fields.Float('Ticket Value')
    other_allowance = fields.Float('Other Allowance')
    remaining_amount_loan =fields.Float(compute='_get_loan',string='Remaining Amount Loan')

    @api.depends('employee_id')
    def _get_loan(self):
        for rec in self:
            loan=self.env['hr.loan'].search([('employee_id','=',rec.employee_id.id),('state','in',['approve','done'])])
            rec.remaining_amount_loan=sum(l.amount_to_pay for l in loan)
    # account
    journal_id = fields.Many2one('account.journal', 'Force Journal', help="The journal used when the eos is done.")
    account_move_id = fields.Many2one('account.move', 'Ledger Posting')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, default=_get_currency)
    year_id = fields.Many2one('year.year', 'Year', required=True, readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, index=True,
                              default=lambda self: self.env['year.year'].find(time.strftime("%Y-%m-%d"), True),
                              ondelete='cascade')
    ticket_account=fields.Many2many('account.account','ticket_rel','t1','t2')
    loan_account=fields.Many2many('account.account','loan_rel','l1','l2')
    other_deduction_account=fields.Many2many('account.account','deduction_rel','d1','d2')
    other_allowance_account=fields.Many2many('account.account','allow_rel','a1','a2')

    ticket_account_id=fields.Many2one('account.account')
    loan_account_id=fields.Many2one('account.account')
    other_deduction_account_id=fields.Many2one('account.account')
    other_allowance_account_id=fields.Many2one('account.account')
    remaining_leave_account_id=fields.Many2one('account.account')
    payment_method=fields.Many2one('eos.method',required=True)

    @api.onchange('payment_method')
    def _onchange_payment_method(self):
        for rec in self:
            rec.ticket_account_id = rec.payment_method.ticket_account_id
            rec.loan_account_id = rec.payment_method.loan_account_id
            rec.other_deduction_account_id = rec.payment_method.other_deduction_account_id
            rec.other_allowance_account_id = rec.payment_method.other_allowance_account_id
            rec.remaining_leave_account_id = rec.payment_method.remaining_leave_account_id

    def _track_subtype(self, init_values):
        """
            Track Subtypes of EOS
        """
        self.ensure_one()
        if 'state' in init_values and self.state == 'draft':
            return self.env.ref('saudi_hr_eos.mt_employee_eos_new')
        elif 'state' in init_values and self.state == 'confirm':
            return self.env.ref('saudi_hr_eos.mt_employee_eos_confirm')
        elif 'state' in init_values and self.state == 'accepted':
            return self.env.ref('saudi_hr_eos.mt_employee_eos_accept')
        elif 'state' in init_values and self.state == 'validate':
            return self.env.ref('saudi_hr_eos.mt_employee_eos_validate')
        elif 'state' in init_values and self.state == 'done':
            return self.env.ref('saudi_hr_eos.mt_employee_eos_done')
        elif 'state' in init_values and self.state == 'cancelled':
            return self.env.ref('saudi_hr_eos.mt_employee_eos_cancel')
        return super(HrEmployeeEos, self)._track_subtype(init_values)

    def copy(self, default=None):
        """
            Duplicate record
        """
        default = dict(default or {})
        default.update(
            account_move_id=False,
            date_confirm=False,
            date_valid=False,
            date_approve=False,
            user_valid=False)
        return super(HrEmployeeEos, self).copy(default=default)

    @api.model
    def create(self, values):
        """
            Create a new Record
        """
        if values.get('employee_id'):
            eos_ids = self.env['hr.employee.eos'].search([('employee_id', '=', values.get('employee_id'))])
            if eos_ids:
                raise UserError(_("%s's EOS is already Generated.") % (eos_ids.employee_id.name))
        return super(HrEmployeeEos, self).create(values)

    def write(self, values):
        """
            update existing record
        """
        if values.get('employee_id'):
            eos_ids = self.env['hr.employee.eos'].search([('employee_id', '=', values.get('employee_id'))])
            if eos_ids:
                raise UserError(_("%s's EOS is already in Generated.") % (eos_ids.employee_id.name))
        return super(HrEmployeeEos, self).write(values)

    def unlink(self):
        """
            Remove record
        """
        for record in self:
            if record.state in ['confirm', 'validate', 'accepted', 'done', 'cancelled']:
                raise UserError(_('You cannot remove the record which is in %s state!') % record.state)
        return super(HrEmployeeEos, self).unlink()

    def onchange_currency_id(self):
        """
            find the journal using currency
        """
        journal_ids = self.env['account.journal'].search([('type', '=', 'purchase'), ('currency_id', '=', self.currency_id.id), ('company_id', '=', self.company_id.id)], limit=1)
        if journal_ids:
            self.journal_id = journal_ids[0].id

    def calc_eos(self):
        """
            Calculate eos
        """
        payslip_obj = self.env['hr.payslip']
        for eos in self:
            if not eos.date_of_leave:
                raise UserError(_('Please define employee date of leaving!'))
            diff = relativedelta.relativedelta(eos.date_of_leave, eos.date_of_join)
            duration_days = diff.days
            duration_months = diff.months
            duration_years = diff.years
            eos.write({'duration_days': duration_days, 'duration_months': duration_months,
                       'duration_years': duration_years})
            selected_month = eos.date_of_leave.month
            selected_year = eos.date_of_leave.year
            date_from = date(selected_year, selected_month, 1)
            date_to = date_from + relativedelta.relativedelta(day=eos.date_of_leave.day)
            # contract_ids = self.payslip_id.employee_id._get_contracts(date_from, date_to, states=['open'])
            contract_ids = self.employee_id._get_contracts(date_from, date_to, states=['open'])
            if not contract_ids:
                raise UserError(_('Please define contract for selected Employee!'))

            # Currently your company contract wage will be calculate as last salary.
            wages = contract_ids[0].basic
            total_eos = 0.0
            if 2 <= duration_years < 5:
                total_eos = ((wages / 2) * duration_years) + (((wages / 2) / 12) * duration_months) + ((((wages/2) / 12) / 30) * duration_days)
            elif 5 <= duration_years < 10:
                total_eos = ((wages / 2) * duration_years) + ((wages / 12) * duration_months) + (((wages / 12) / 30) * duration_days)
            elif duration_years >= 10:
                total_eos = ((wages / 2) * 5) + (wages * (duration_years - 5)) + ((wages / 12) * duration_months) + ((wages / 365) * duration_days)
            if not eos.journal_id:
                raise UserError(_('Please configure Journal before calculating EOS.'))
            values = {
                'name': eos.employee_id.name,
                'employee_id': eos.employee_id.id or False,
                'date_from': date_from,
                'date_to': date_to,
                'contract_id': contract_ids[0].id,
                # 'struct_id': eos.contract_id.struct_id.id or False,
                # 'journal_id': eos.journal_id.id or False,
            }
            if not eos.payslip_id:
                payslip_id = payslip_obj.create(values)
                eos.write({'payslip_id': payslip_id.id})
            # eos.payslip_id._onchange_employee()
            eos.payslip_id._onchange_employee()
            eos.payslip_id.compute_sheet()
            net = 0.00
            payslip_line_obj = self.env['hr.payslip.line']
            net_rule_id = payslip_line_obj.search([('slip_id', '=', eos.payslip_id.id),
                                                   ('code', 'ilike', 'NET')])
            if net_rule_id:
                net_rule_obj = net_rule_id[0]
                net = net_rule_obj.total
            eos.write({'current_month_salary': net})
            payable_eos = total_eos
            if eos.type == 'resignation':
                if 2 < eos.calc_year < 5:
                    payable_eos = total_eos / 3
                elif 5 < eos.calc_year < 10:
                    payable_eos = (total_eos * 2) / 3
                elif eos.calc_year > 10:
                    payable_eos = total_eos
            # Annual Leave Calc
            holiday_status_ids = self.env['hr.leave.type'].search([('is_annual_leave', '=', True)], limit=1)
            if holiday_status_ids:
                leave_values = holiday_status_ids.get_days(eos.employee_id.id) # eos.year_id.id
                leaves_taken = leave_values[holiday_status_ids[0].id]['leaves_taken']
                diff_date = relativedelta.relativedelta(eos.date_of_leave, eos.year_id.date_start)

                allocate_leave_month = diff_date.months * eos.job_id.annual_leave_rate
                #remaining_leaves = allocate_leave_month - leaves_taken
                annual_leaving_id = self.env['annual.leaving'].search([('year_id', '=', eos.year_id.id)], limit=1)

                leave_details_id = self.env['leaves.details'].search(
                    [('annual_leaving_id', '=', annual_leaving_id.id), ('employee_id', '=', eos.employee_id.id)])
                time_request = self.env['hr.leave'].search(
                    [('state', '=', 'validate'), ('employee_id', '=', self.employee_id.id),
                     ('holiday_status_id.is_annual_leave', '=',True)])
                time_off_days = sum(request.number_of_days for request in time_request)
                allocation = self.env['hr.leave.allocation'].search(
                    [('state', '=', 'validate'), ('employee_id', '=', self.employee_id.id),
                     ('holiday_status_id.is_annual_leave', '=',True)])
                number_of_days_allocation = sum(all.number_of_days for all in allocation)
                remaining_leaves = number_of_days_allocation - time_off_days
                # remaining_leaves = allocate_leave_month - leaves_taken

                annual_leave_amount = (wages / 30) * remaining_leaves
                eos.write({'total_eos': payable_eos, 'annual_leave_amount': annual_leave_amount,
                           'remaining_leave': remaining_leaves})
            return True

    @api.onchange('employee_id', 'eos_date')
    def onchange_employee_id(self):
        """
            Calculate total no of year, month, days, etc depends on employee
        """
        if self.employee_id:
            if not self.employee_id.date_of_leave:
                raise UserError(_('Please define employee date of leaving!'))
            if not self.employee_id.date_of_join:
                raise UserError(_('Please define employee date of join!'))
            selected_date = self.employee_id.date_of_leave
            date_from = date(selected_date.year, selected_date.month, 1)
            date_to = date_from + relativedelta.relativedelta(day=selected_date.day)
            contract_ids = self.employee_id._get_contracts(date_from, date_to, states=['open'])
            if not contract_ids:
                raise UserError(_('Please define contract for selected Employee!'))
            calc_years = round(((self.employee_id.date_of_leave - self.employee_id.date_of_join).days / 365.0), 2)
            diff = relativedelta.relativedelta(self.employee_id.date_of_leave, self.employee_id.date_of_join)
            self.contract_id = contract_ids[0]
            self.date_of_leave = self.employee_id.date_of_leave
            self.date_of_join = self.employee_id.date_of_join
            self.calc_year = calc_years
            self.department_id = self.employee_id.department_id.id or False
            self.company_id = self.employee_id.company_id.id or False
            self.job_id = self.employee_id.sudo().job_id.id or False
            self.duration_years = diff.years or 0
            self.duration_months = diff.months or 0
            self.duration_days = diff.days or 0

    def eos_confirm(self):
        """
            EOS confirm state.
        """
        self.ensure_one()
        self.write({'state': 'confirm',
                    'date_confirm': time.strftime('%Y-%m-%d')})
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('EOS Confirmed.'))

    def eos_validate(self):
        """
            EOS validate state.
        """
        self.ensure_one()
        # finance_groups_config_obj = self.env['hr.groups.configuration']
        for record in self:
            record.calc_eos()
            # finance_groups_config_ids = finance_groups_config_obj.search([('branch_id', '=', record.employee_id.branch_id.id or False), ('finance_ids', '!=', False)])
            # partner_ids = finance_groups_config_ids and [item.user_id.partner_id.id for item in finance_groups_config_ids.finance_ids if item.user_id] or []
            partner_ids=[]
            if record.employee_id.parent_id.user_id:
                partner_ids.append(record.employee_id.parent_id.user_id.partner_id.id)
            record.message_subscribe(partner_ids=partner_ids)
        self.write({'state': 'validate',
                    'date_valid': time.strftime('%Y-%m-%d'),
                    'user_valid': self.env.uid})
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('EOS Validated.'))

    def eos_accept(self):
        """
            EOS accept state
        """
        self.ensure_one()
        self.write({'state': 'accepted',
                    'date_approve': time.strftime('%Y-%m-%d'),
                    'user_approve': self.env.uid})
        self.message_post(message_type="email",subtype_xmlid='mail.mt_comment', body=_('EOS Approved.'))

    def eos_cancelled(self):
        """
            EOS confirm state
        """
        self.ensure_one()
        self.state = 'cancelled'
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('EOS Cancelled.'))

    def eos_draft(self):
        """
            EOS set to draft state
        """
        self.ensure_one()
        self.state = 'draft'
        self.message_post(message_type="email",subtype_xmlid='mail.mt_comment', body=_('EOS Draft.'))

    def action_receipt_create(self):
        """
            main function that is called when trying to create the accounting entries related to an expense
        """
        debit_vals=[]
        credit_vals=[]
        for eos in self:
            if not eos.employee_id.address_home_id:
                    raise UserError(_('The employee must have a home address.'))
            if not eos.employee_id.address_home_id.property_account_payable_id.id:
                raise UserError(_('The employee must have a payable account set on his home address.'))
            company_currency = eos.company_id.currency_id.id
            diff_currency_p = eos.currency_id.id != company_currency
            eml = []
            if not eos.journal_id:
                raise UserError(_('Please configure employee EOS for journal.'))
            timenow = time.strftime('%Y-%m-%d')
            amount = 0.0
            amount -= eos.total_eos
            eos_name = eos.name.split('\n')[0][:64]
            reference = eos.name
            journal_id = eos.journal_id.id
            credit_account_id = eos.journal_id.default_account_id.id
            debit_account_id = eos.employee_id.address_home_id.property_account_payable_id.id
            credit_account_payable = eos.employee_id.address_home_id.property_account_payable_id.id
            if not credit_account_id:
                raise UserError(_("Please configure %s journal's credit account.") % eos.journal_id.name)
            debit_vals.append({
                'name': 'Total EOS',
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'partner_id': eos.employee_id.address_home_id.id,
                'date': timenow,
                'debit': eos.total_eos > 0.0 and eos.total_eos or 0.0,
                'credit': eos.total_eos < 0.0 and -eos.total_eos or 0.0,
                # 'branch_id': eos.employee_id.branch_id.id or False,
                'analytic_account_id': eos.contract_id.analytic_account_id.id or False,
                'analytic_tag_ids': [(6, 0, eos.contract_id.analytic_tag_ids.ids)] or False,
            })
            debit_vals.append({
                'name': 'Annual Leave',
                'account_id': eos.remaining_leave_account_id.id,
                'journal_id': journal_id,
                'partner_id': eos.employee_id.address_home_id.id,
                'date': timenow,
                'debit': eos.annual_leave_amount > 0.0 and eos.annual_leave_amount or 0.0,
                'credit': eos.annual_leave_amount < 0.0 and -eos.annual_leave_amount or 0.0,
                # 'branch_id': eos.employee_id.branch_id.id or False,
                'analytic_account_id': eos.contract_id.analytic_account_id.id or False,
                'analytic_tag_ids': [(6, 0, eos.contract_id.analytic_tag_ids.ids)] or False,
            })
            debit_vals.append({
                'name': 'Ticket Value',
                'account_id': eos.ticket_account_id.id,
                'journal_id': journal_id,
                'partner_id': eos.employee_id.address_home_id.id,
                'date': timenow,
                'debit': eos.ticket_value  > 0.0 and eos.ticket_value  or 0.0,
                'credit': eos.ticket_value  < 0.0 and -eos.ticket_value or 0.0,
                # 'branch_id': eos.employee_id.branch_id.id or False,
                'analytic_account_id': eos.contract_id.analytic_account_id.id or False,
                'analytic_tag_ids': [(6, 0, eos.contract_id.analytic_tag_ids.ids)] or False,
            })
            debit_vals.append({
                'name':'Other Allowance',
                'account_id': eos.other_allowance_account_id.id,
                'journal_id': journal_id,
                'partner_id': eos.employee_id.address_home_id.id,
                'date': timenow,
                'debit': eos.other_allowance  > 0.0 and eos.other_allowance or 0.0,
                'credit': eos.other_allowance  < 0.0 and -eos.other_allowance or 0.0,
                # 'branch_id': eos.employee_id.branch_id.id or False,
                'analytic_account_id': eos.contract_id.analytic_account_id.id or False,
                'analytic_tag_ids': [(6, 0, eos.contract_id.analytic_tag_ids.ids)] or False,
            })
            total_payable=((eos.total_eos + eos.annual_leave_amount + eos.ticket_value + eos.other_allowance) - (
                        eos.others + eos.remaining_amount_loan))
            debit_vals.append({
                'name': 'Remaining Loan',
                'account_id': eos.loan_account_id.id,
                'partner_id': eos.employee_id.address_home_id.id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': eos.remaining_amount_loan < 0.0 and -eos.remaining_amount_loan or 0.0,
                'credit': eos.remaining_amount_loan > 0.0 and eos.remaining_amount_loan or 0.0,
                # 'branch_id': eos.employee_id.branch_id.id or False,
                'analytic_account_id': eos.contract_id.analytic_account_id.id or False,
                'analytic_tag_ids': [(6, 0, eos.contract_id.analytic_tag_ids.ids)] or False,
            })
            debit_vals.append({
                'name': 'Total Payable',
                'account_id':eos.other_deduction_account_id.id,
                'partner_id': eos.employee_id.address_home_id.id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': eos.others < 0.0 and -eos.others  or 0.0,
                'credit': eos.others  > 0.0 and eos.others or 0.0,
                # 'branch_id': eos.employee_id.branch_id.id or False,
                'analytic_account_id': eos.contract_id.analytic_account_id.id or False,
                'analytic_tag_ids': [(6, 0, eos.contract_id.analytic_tag_ids.ids)] or False,
            })
            debit_vals.append({
                'name': eos_name,
                'account_id':credit_account_payable,
                'partner_id': eos.employee_id.address_home_id.id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': total_payable < 0.0 and -total_payable  or 0.0,
                'credit': total_payable  > 0.0 and total_payable or 0.0,
                # 'branch_id': eos.employee_id.branch_id.id or False,
                'analytic_account_id': eos.contract_id.analytic_account_id.id or False,
                'analytic_tag_ids': [(6, 0, eos.contract_id.analytic_tag_ids.ids)] or False,
            })
            vals = {
                'name': '/',
                'narration': eos_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                # 'branch_id': eos.employee_id.branch_id.id or False,
                'line_ids': [(0, 0, d)for d in debit_vals]
            }
            move = self.env['account.move'].create(vals)
            move.post()
            self.write({'account_move_id': move.id, 'state': 'done'})

    # def account_move_get(self):
    #     """
    #         This method prepare the creation of the account move related to the given expense.
    #
    #         :param eos_id: Id of voucher for which we are creating account_move.
    #         :return: mapping between field name and value of account move to create
    #         :rtype: dict
    #     """
    #     self.ensure_one()
    #     journal_obj = self.env['account.journal']
    #     company_id = self.company_id.id
    #     date = self.date_confirm
    #     ref = self.name
    #     if self.journal_id:
    #         journal_id = self.journal_id.id
    #     else:
    #         journal_id = journal_obj.search([('type', '=', 'purchase'), ('company_id', '=', company_id)])
    #         if not journal_id:
    #             raise UserError(_("No EOS journal found. "
    #                               "Please make sure you have a journal with type 'purchase' configured."))
    #         journal_id = journal_id[0].id
    #     return self.env['account.move'].account_move_prepare(journal_id, date=date, ref=ref, company_id=company_id)
    #
    # def line_get_convert(self, x, part, date):
    #     """
    #         line get convert
    #     """
    #     partner_id = self.env['res.partner']._find_accounting_partner(part).id
    #     return {
    #         'date_maturity': x.get('date_maturity', False),
    #         'partner_id': partner_id,
    #         'name': x['name'][:64],
    #         'date': date,
    #         'debit': x['price'] > 0 and x['price'],
    #         'credit': x['price'] < 0 and -x['price'],
    #         'account_id': x['account_id'],
    #         'analytic_lines': x.get('analytic_lines', False),
    #         'amount_currency': x['price'] > 0 and abs(x.get('amount_currency', False)) or -abs(x.get('amount_currency', False)),
    #         'currency_id': x.get('currency_id', False),
    #         'tax_code_id': x.get('tax_code_id', False),
    #         'tax_amount': x.get('tax_amount', False),
    #         'ref': x.get('ref', False),
    #         'quantity': x.get('quantity', 1.00),
    #         'product_id': x.get('product_id', False),
    #         'product_uom_id': x.get('uos_id', False),
    #         'analytic_account_id': x.get('account_analytic_id', False),
    #     }
    #
    # def action_receipt_create(self):
    #     """
    #         main function that is called when trying to create the accounting entries related to an expense
    #     """
    #     for eos in self:
    #         if not eos.employee_id.address_home_id:
    #             raise UserError(_('The employee must have a home address.'))
    #         if not eos.employee_id.address_home_id.property_account_payable_id.id:
    #             raise UserError(_('The employee must have a payable account set on his home address.'))
    #         company_currency = eos.company_id.currency_id.id
    #         diff_currency_p = eos.currency_id.id != company_currency
    #         eml = []
    #         if not eos.journal_id:
    #             raise UserError(_('Please configure employee EOS for journal.'))
    #
    #         move_id = self.env['account.move'].create({'journal_id': eos.journal_id.id,
    #                                                    'company_id': eos.env.user.company_id.id})
    #
    #         # create the move that will contain the accounting entries
    #         ctx = self._context.copy()
    #         ctx.update({'force_company': eos.company_id.id})
    #         acc = self.env['ir.property'].with_context(ctx).get('property_account_expense_categ_id', 'product.category')
    #         if not acc:
    #             raise UserError(_('Please configure Default Expense account for Product purchase: `property_account_expense_categ`.'))
    #         acc1 = eos.employee_id.address_home_id.property_account_payable_id
    #         eml.append({'type': 'src',
    #                     'name': eos.name.split('\n')[0][:64],
    #                     'price': eos.payable_eos,
    #                     'account_id': acc.id,
    #                     'date_maturity': eos.date_confirm
    #                     })
    #         total = 0.0
    #         total -= eos.payable_eos
    #         eml.append({
    #                 'type': 'dest',
    #                 'name': '/',
    #                 'price': total,
    #                 'account_id': acc1.id,
    #                 'date_maturity': eos.date_confirm,
    #                 'amount_currency': diff_currency_p and eos.currency_id.id or False,
    #                 'currency_id': diff_currency_p and eos.currency_id.id or False,
    #                 'ref': eos.name,
    #                 # 'move_id': move_id.id,
    #                 })
    #
    #         # convert eml into an osv-valid format
    #         account_move_line_obj = self.env['account.move.line']
    #         for line in eml:
    #              a = account_move_line_obj.create(line)
    #         # lines = map(lambda x: (0, 0, self.line_get_convert(x, eos.employee_id.address_home_id, eos.date_confirm)), eml)
    #         # journal_id = move_obj.browse(cr, uid, move_id, context).journal_id
    #
    #         # post the journal entry if 'Skip 'Draft' State for Manual Entries' is checked
    #         # if journal_id.entry_posted:
    #         #     move_obj.button_validate(cr, uid, [move_id], context)
    #
    #         # move_id.write({'line_ids': lines})
    #         self.write({'account_move_id': move_id.id, 'state': 'done'})
    #     return True

    def action_view_receipt(self):
        """
            This function returns an action that display existing account.move of given expense ids.
        """
        assert len(self.ids) == 1, 'This option should only be used for a single id at a time'
        self.ensure_one()
        assert self.account_move_id
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('account', 'view_move_form')
        except ValueError:
            view_id = False
        result = {
            'name': _('EOS Account Move'),
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': self.account_move_id.id,
        }
        return result


class HrJob(models.Model):
    _inherit = 'hr.job'
    _description = 'HR Job'

    annual_leave_rate = fields.Float('Annual Leave Rate', default=2)
