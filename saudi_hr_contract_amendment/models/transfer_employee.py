# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import time


class TransferEmployee(models.Model):
    _inherit = ['mail.thread', 'analytic.mixin']
    _name = 'transfer.employee'
    _description = "Transfer Employee"

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, default=lambda self: self.env['hr.employee'].get_employee())
    hr_contract_id = fields.Many2one('hr.contract', 'Contract', required=True, domain="[('employee_id', '=', employee_id)]")
    job_id = fields.Many2one('hr.job', 'From Job', readonly=True)
    department_id = fields.Many2one('hr.department', 'From Department', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    branch_id = fields.Many2one('hr.branch', 'From Office', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', readonly=True)
    effective_date = fields.Date('Effective Date', default=time.strftime('%Y-%m-%d'))
    new_department_id = fields.Many2one('hr.department', 'To Department')
    new_job_id = fields.Many2one('hr.job', 'To Job')
    new_branch_id = fields.Many2one('hr.branch', 'To Office')
    new_analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Waiting Manager Approval'),
        ('validate', 'Waiting HR department Approval'),
        ('approve', 'Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancel')], 'State', default='draft', tracking=True)
    description = fields.Text('Description')
    approved_date = fields.Datetime('Approved Date', readonly=True, copy=False)
    approved_by = fields.Many2one('res.users', 'Approved by', readonly=True, copy=False)
    validated_by = fields.Many2one('res.users', 'Validated by', readonly=True, copy=False)
    validated_date = fields.Datetime('Validated Date', readonly=True, copy=False)
    new_analytic_distribution = fields.Json(
        'New Analytic',
        compute="_compute_analytic_distribution", store=True, copy=True, readonly=False,
    )

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            onchange the value of department_id, job_id, hr_contract_id based on employee_id,
        """
        if self.employee_id:
            effective_date = time.strftime('%Y-%m-%d')
            payslip_obj = self.env['hr.payslip']
            contract_ids = self.employee_id._get_contracts(effective_date, effective_date, states=['open'])
            if not contract_ids:
                self.employee_id = False
                raise UserError(_('Please define contract for selected Employee!'))
            contract = payslip_obj.browse(contract_ids)
            self.department_id = self.employee_id.department_id.id or False
            self.branch_id = self.employee_id.branch_id.id or False
            self.job_id = self.employee_id.job_id.id or False
            self.hr_contract_id = contract and contract[0].id or False
            if contract_ids:
                self.analytic_account_id = contract_ids[0].analytic_account_id and contract_ids[0].analytic_account_id.id or False
                self.analytic_distribution = contract_ids[0].analytic_distribution

    @api.onchange('new_department_id')
    def onchange_department(self):
        """
            onchange the value of new_job_id based on new_department_id,
        """
        self.new_job_id = False

    @api.depends('employee_id')
    def name_get(self):
        """
            Return name of employee.
        """
        result = []
        for transfer in self:
            name = transfer.employee_id.name or ''
            result.append((transfer.id, name))
        return result

    def unlink(self):
        """
            Delete/ remove selected record
            :return: Deleted record ID
        """
        for objects in self:
            if objects.state in ['confirm', 'validate', 'approve', 'done', 'cancel']:
                raise UserError(_('You cannot remove the record which is in %s state!') % objects.state)
        return super(TransferEmployee, self).unlink()

    def _add_followers(self):
        """
            Add employee and manager in followers
        """
        partner_ids = []
        if self.employee_id.user_id:
            partner_ids.append(self.employee_id.user_id.partner_id.id)
        if self.employee_id.parent_id.user_id:
            partner_ids.append(self.employee_id.parent_id.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner_ids)

    def transfer_confirm(self):
        """
            sent the status of generating contract amendment record in confirmed state
        """
        self.ensure_one()
        warnings = self.env['issue.warning'].search([
            ('id', 'in', self.employee_id.issue_warning_ids.ids), ('warning_action', '=', 'prohibit'), ('state', '=', 'done')])
        for warning in warnings:
            if self.effective_date >= warning.start_date and self.effective_date <= warning.end_date:
                raise UserError(_("You can't Confirm Contract Amendment because %s have Prohibit Benefit Upgrades Warning.") % self.employee_id.name)
        self.state = 'confirm'

    def transfer_validate(self):
        """
            sent the status of generating contract amendment record in validate state
        """
        self.ensure_one()
        hop_groups_config_obj = self.env['hr.groups.configuration']
        hop_groups_config_ids = hop_groups_config_obj.search([('branch_id', '=', self.employee_id.branch_id.id or False), ('hop_ids', '!=', False)])
        partner_ids = hop_groups_config_ids and [employee.user_id.partner_id.id for employee in hop_groups_config_ids.hop_ids if employee.user_id] or []
        self.message_subscribe(partner_ids)
        today = datetime.today()
        user = self.env.user
        self.write({'state': 'validate',
                    'validated_by': user.id,
                    'validated_date': today})

    def transfer_approve(self):
        """
            sent the status of generating contract amendment record in Approve state
        """
        self.ensure_one()
        today = datetime.today()
        user = self.env.user
        self.write({'state': 'approve',
                    'approved_by': user.id,
                    'approved_date': today})

    def get_employee_data(self, employee_id, contract=False):
        """
            Update employee department, branch, job based on effective date
        """
        if contract:
            employee_id.write({'department_id': contract.new_department_id.id or False,
                               'branch_id': contract.new_branch_id.id or False,
                               'job_id': contract.new_job_id.id or False})
        else:
            employee_id.write({'department_id': self.new_department_id.id or False,
                               'branch_id': self.new_branch_id.id or False,
                               'job_id': self.new_job_id.id or False})

    def transfer_done(self):
        """
            sent the status of generating record his/her contract amendment in 'done' state
        """
        self.ensure_one()
        if self.effective_date <= datetime.today().date():
            if self.hr_contract_id.date_end and self.effective_date >= self.hr_contract_id.date_end:
                vals = {'name': self.employee_id.name,
                        'department_id': self.new_department_id.id or False,
                        'job_id': self.new_job_id.id or False,
                        'employee_id': self.employee_id.id,
                        'analytic_account_id': self.new_analytic_account_id and self.new_analytic_account_id.id or False,
                        'analytic_distribution': self.new_analytic_distribution,
                        'date_start': self.effective_date,
                        'wage': 0.0
                        }
                self.env['hr.contract'].create(vals)
            else:
                self.hr_contract_id.write({'department_id': self.new_department_id.id or False,
                                           'job_id': self.new_job_id.id or False,
                                           'analytic_account_id': self.new_analytic_account_id and self.new_analytic_account_id.id or False,
                                           'analytic_distribution': self.new_analytic_distribution,})
            self.get_employee_data(self.employee_id)
            self.state = 'done'
            try:
                template_id = self.env.ref('saudi_hr_contract_amendment.hr_contract_amendment_updation_email')
            except ValueError:
                template_id = False
            if template_id:
                grade = False
                if dict(self._fields).get('grade_id', False):
                    grade = True
                template_id.with_context({'grade': grade}).send_mail(self.id, force_send=True, raise_exception=False)
        else:
            raise ValidationError(_('You Can not Done the Contract Amendment Because Effective Date is %s.') % self.effective_date)

    def check_contract_amendment_effective_date(self):
        """
            Update employee details based on contract amendment effective date
        """
        try:
            template_id = self.env.ref('saudi_hr_contract_amendment.hr_contract_amendment_updation_email')
        except ValueError:
            template_id = False
        contract_amendment = self.search([('effective_date', '=', datetime.today()), ('state', '=', 'approve')])
        for contract in contract_amendment:
            if contract.hr_contract_id and contract.hr_contract_id.date_end and contract.effective_date >= contract.hr_contract_id.date_end:
                vals = {'name': contract.employee_id.name,
                        'department_id': contract.new_department_id.id or False,
                        'job_id': contract.new_job_id.id or False,
                        'analytic_account_id': self.new_analytic_account_id and self.new_analytic_account_id.id or False,
                        'analytic_distribution': self.analytic_distribution,
                        'employee_id': contract.employee_id.id,
                        'date_start': contract.effective_date,
                        'wage': 0.0
                        }
                self.env['hr.contract'].create(vals)
            else:
                contract.hr_contract_id.write({'department_id': contract.new_department_id.id or False,
                                               'job_id': contract.new_job_id.id or False,
                                               'analytic_account_id': self.new_analytic_account_id and self.new_analytic_account_id.id or False,
                                               'analytic_distribution': self.analytic_distribution})
            if contract.employee_id:
                self.get_employee_data(contract.employee_id, contract)
                contract.state = 'done'
                if template_id:
                    grade = False
                    if dict(self._fields).get('grade_id', False):
                        grade = True
                    template_id.with_context({'grade': grade}).send_mail(contract.id, force_send=True, raise_exception=False)

    def transfer_cancel(self):
        """
            sent the status of generating contract amendment record in Cancel state
        """
        self.ensure_one()
        self.state = 'cancel'

    def set_to_draft(self):
        """
            sent the status of generating contract amendment record in draft state
        """
        self.ensure_one()
        self.employee_id.department_id = self.department_id.id or False
        self.employee_id.branch_id = self.branch_id.id or False
        self.employee_id.job_id = self .job_id.id or False
        self.write({'state': 'draft',
                    'approved_by': False,
                    'approved_date': False,
                    'validated_by': False,
                    'validated_date': False})



class HRContract(models.Model):
    _name = 'hr.contract' 
    _inherit = ['hr.contract', 'mail.thread']

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 
        string='Account Name', 
        ondelete="cascade",
        required=True, 
        index=True, 
        help="Link contract to an analytic account.It enables you to connect contracts with budgets, planning, cost and revenue analysis,timesheets on contracts, etc.")