# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import time
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _


class EmployeeBonus(models.Model):
    _name = "employee.bonus"
    _inherit = ['mail.thread']
    _description = "Employee Bonus"
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    country_id = fields.Many2one('res.country', string='Nationality', readonly=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender', readonly=True)
    date_of_join = fields.Date(string='Joining Date', readonly=True)
    job_id = fields.Many2one('hr.job', string='Job Position', readonly=True)
    department_id = fields.Many2one('hr.department', readonly=True, string='Department')
    branch_id = fields.Many2one('hr.branch', 'Office', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    no_of_months = fields.Float(string='Number of Months', help="Total number of months")
    employee_bonus_ids = fields.One2many('employee.bonus.lines', 'employee_bonus_id')
    approved_date = fields.Datetime(string='Approved Date', readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved by', readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting for Approval'),
                              ('approve', 'Approved')], string='Status', readonly=True, default='draft', help="Gives the status of Employee Bonus.", tracking=True)

    @api.constrains('state', 'employee_id')
    def check_duplicate_record(self):
        """
            Constraints for the bonus is overlaps for same employee or not.
        """
        rec = self.search_count([('state', '=', 'approve'), ('employee_id', '=', self.employee_id.id), ('id', '!=', self.id)])
        if rec:
            raise ValidationError(_('You already create bonus record for this employee, Kindly check!!'))

    def action_button_confirm(self):
        """
            sent the status of generating record his/her bonus in 'confirm' state
        """
        self.ensure_one()
        self.state = 'confirm'
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Bonus Confirmed.'))

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            onchange the value based on selected employee,
            country, gender, joining date, job, department
        """
        self.country_id = False
        self.gender = False
        self.date_of_join = False
        self.job_id = False
        self.department_id = False
        self.branch_id = False
        if self.employee_id:
            self.country_id = self.employee_id.country_id.id
            self.gender = self.employee_id.gender
            self.date_of_join = self.employee_id.date_of_join
            self.job_id = self.employee_id.job_id.id
            self.department_id = self.employee_id.department_id.id
            self.branch_id = self.employee_id.branch_id.id

    def action_set_to_draft(self):
        """
            sent the status of generating record his/her bonus in 'draft' state
        """
        self.ensure_one()
        self.write({'state': 'draft',
                    'approved_by': False,
                    'approved_date': False
                    })
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Bonus Set to Draft.'))

    def action_button_validate(self):
        """
            sent the status of generating record his/her bonus in 'approve' state
        """
        self.ensure_one()
        self.write({'state': 'approve',
                    'approved_by': self.env.uid,
                    'approved_date': datetime.today()
                    })
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Bonus Approved.'))

    def unlink(self):
        """
            To remove the record, which is not in 'done' state
        """
        for rec in self:
            for line in rec.employee_bonus_ids:
                if line.state == 'done':
                    raise UserError(_('You can not delete the record for which process is already done!'))
        return super(EmployeeBonus, self).unlink()


class EmployeeBonusLines(models.Model):
    _name = "employee.bonus.lines"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "employee_id"
    _description = "Employee Bonus Lines"

    @api.model
    def default_get(self, fields):
        """
            Default Get From Bonus line.
        """
        data = super(EmployeeBonusLines, self).default_get(fields)
        if self._context.get('employee_id', False):
            employee_id = self.env['hr.employee'].browse(self._context.get('employee_id'))
            data.update({'employee_id': employee_id.id,
                         'job_id': self._context.get('job_id', False)})
            fiscal_year = data.get('fiscalyear_id') and self.env['year.year'].browse(data.get('fiscalyear_id'))
            if fiscal_year:
                contract_ids = self.employee_id._get_contracts(fiscal_year.date_start, fiscal_year.date_stop, states=['open'])
                if contract_ids:
                    wage_amt = contract_ids and self.env['hr.contract'].browse(contract_ids[0]).wage
                    data.update({
                        'wage': wage_amt,
                        'contract_id': contract_ids and contract_ids[0],
                    })
        return data

    @api.depends('bonus')
    def _get_bonus_amount(self):
        """
            Check the values of bonus if bonus > 0, increase is true or false
        """
        if self.bonus > 0:
            self.is_increase = True
        else:
            self.is_increase = False

    employee_id = fields.Many2one('hr.employee', string='Employee')
    fiscalyear_id = fields.Many2one('year.year', string='Fiscal Year', required=True, default=lambda self: self.env['year.year'].find(time.strftime("%Y-%m-%d"), True))
    period_ids = fields.Many2many('year.period', string='Month(s)', help='Specify month(s) in which the bonus will be distributed. Bonus will be distributed in Bonus Amount/Number of Month(s).')
    wage = fields.Float(string='Wage', digits=(16, 2), help="Basic salary of the employee")
    job_id = fields.Many2one('hr.job', string='Job Position')
    new_job_id = fields.Many2one('hr.job', string='New Job Position', required=True)
    effective_date = fields.Date(string='Effective Date', required=True)
    proposed_hike = fields.Float(string='Proposed Hike(%)', digits=(16, 2), required=True, help="Proposed hike on basic salary of the employee")
    proposed_amount = fields.Float(string='Proposed Amount', digits=(16, 2), readonly=True, help="Proposed amount on basic salary of the employee")
    accepted_hike = fields.Float(string='Accepted Hike(%)', digits=(16, 2), help="Accepted hike on basic salary of the employee")
    accepted_amount = fields.Float(string='Accepted Amount', digits=(16, 2), readonly=True, help="Accepted amount on basic salary of the employee")
    bonus = fields.Float(string='Bonus', digits=(16, 2), required=True, help="Bonus to the employee")
    bonus_percentage = fields.Float(string='Bonus(%)', digits=(16, 2), readonly=True, help="Bonus(%) to the employee")
    employee_bonus_id = fields.Many2one('employee.bonus', string='Employee Bonus', ondelete="cascade", default=lambda self: self.env.context.get('employee_bonus_id', False))
    tcc = fields.Float(string='TCC', digits=(16, 2), help="TCC(Total Cash Compensation) of the employee")
    dialogue = fields.Char(string='Dialogue')
    my_pd = fields.Selection([('1 - Outstanding Performance', '1 - Outstanding Performance'),
                              ('2 - Highly Effective Performance', '2 - Highly Effective Performance'),
                              ('3 - Effective Performance', '3 - Effective Performance'),
                              ('4 - Inconsistent Performance', '4 - Inconsistent Performance')], string='Performance Development')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting for Approval'),
                              ('approve', 'Approved'),
                              ('cancel', 'Cancelled'),
                              ('done', 'Done')], string='Status', readonly=True, default='draft', help="Gives the status of Employee Bonus.", tracking=True)
    contract_id = fields.Many2one('hr.contract', string='Contract')
    is_increase = fields.Boolean(compute=_get_bonus_amount, string='Is Increase')
    approved_date = fields.Datetime(string='Approved Date', readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved by', readonly=True)

    @api.onchange('proposed_hike', 'wage')
    def onchange_proposed_hike(self):
        """
            onchange the value based on selected proposed hike,
            proposed amount
        """
        if self.wage > 0 and self.proposed_hike > 0:
            proposed_amount = self.wage + (self.wage * self.proposed_hike) / 100
            self.proposed_amount = proposed_amount

    @api.onchange('accepted_hike', 'wage')
    def onchange_accepted_hike(self):
        """
            onchange the value based on selected accepted hike,
            accepted amount
        """
        if self.wage > 0 and self.accepted_hike > 0:
            accepted_amount = self.wage + (self.wage * self.accepted_hike) / 100
        else:
            accepted_amount = 0
        self.accepted_amount = accepted_amount

    @api.onchange('bonus', 'effective_date', 'wage')
    def onchange_bonus(self):
        """
            onchange the value based on selected bonus,
            bonus percentage
        """
        if self.wage > 0 and self.bonus > 0:
            bonus_perc = (self.bonus * 100) / self.wage
            self.bonus_percentage = bonus_perc
            period_id = self.env['year.period'].find(dt=self.effective_date, fiscalyear_id=False, exception=True)
            self.period_ids = period_id.ids

    # ===========================================================================
    # @api.onchange('fiscalyear_id')
    # def onchange_fiscalyear(self):
    #     '''
    #         calculate the wage and contract duration depends on fiscal year
    #     '''
    #     if self.employee_id and self.fiscalyear_id:
    #         contract_ids = self.env['hr.payslip']._get_contract(self.employee_id, self.fiscalyear_id.date_start, self.fiscalyear_id.date_stop)
    #         if contract_ids:
    #             wage_amt = contract_ids and self.env['hr.contract'].browse(contract_ids[0]).wage
    #             self.wage = wage_amt
    #             self.contract_id = contract_ids and contract_ids[0]
    #         else:
    #             self.wage = 0.0
    #             self.contract_id = False
    # ===========================================================================

    @api.onchange('employee_id', 'fiscalyear_id')
    def onchange_employee(self):
        """
            onchange the value based on selected employee, fiscalyear,
            wage, contract
        """
        self.wage = 0.0
        self.contract_id = False
        if self.employee_id:
            contract_ids = self.employee_id._get_contracts(self.fiscalyear_id.date_start, self.fiscalyear_id.date_stop, states=['open'])
            if contract_ids:
                self.contract_id = contract_ids[0]
                self.wage = self.contract_id.wage

    @api.onchange('contract_id')
    def onchange_contract(self):
        """
            onchange the value based on selected contract,
            job, new job and wage
        """
        self.wage = 0.0
        if self.contract_id:
            self.wage = self.contract_id.wage

    def action_button_confirm(self):
        """
            sent the status of generating record his/her bonus in 'confirm' state
        """
        self.ensure_one()
        warnings = self.env['issue.warning'].search([('id', 'in', self.employee_id.issue_warning_ids.ids), ('warning_action', '=', 'prohibit'), ('state', '=', 'done')])
        for warning in warnings:
            if self.effective_date >= warning.start_date and self.effective_date <= warning.end_date:
                raise UserError(_("You can't Confirm Bonus Line because %s have Prohibit Benefit Upgrades Warning.") % self.employee_id.name)
        self.state = 'confirm'
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Bonus Confirmed.'))

    def set_to_draft(self):
        """
            sent the status of generating record his/her bonus in 'draft' state
        """
        self.ensure_one()
        self.write({'state': 'draft',
                    'approved_by': False,
                    'approved_date': False
                    })
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Bonus Set to Draft.'))

    def action_button_approve(self):
        """
            sent the status of generating record his/her bonus in 'approve' state
        """
        self.ensure_one()
        self.write({'state': 'approve',
                    'approved_by': self.env.uid,
                    'approved_date': datetime.today()})
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Bonus Approved.'))

    def action_button_cancel(self):
        """
            sent the status of generating record his/her bonus in 'cancel' state
        """
        self.ensure_one()
        self.state = 'cancel'
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Bonus Cancelled.'))

    def get_employee_data(self, line):
        """
            return employees job_id
        """
        emp_data = {'job_id': line.new_job_id.id}
        return emp_data

    def get_contract_data(self, line):
        """
            return employees contract data
        """
        contract_data = {'job_id': line.new_job_id.id}
        if line.accepted_amount != 0.0:
            contract_data.update({'wage': line.accepted_amount})
        elif line.proposed_amount != 0.0:
            contract_data.update({'wage': line.proposed_amount})
        return contract_data

    def check_bonus_effective_date(self):
        """
            Update contract based on effective date
        """
        try:
            template_id = self.env.ref('saudi_hr_bonus.hr_bonus_contract_updation_email')
        except ValueError:
            template_id = False
        bonus_lines = self.search([('effective_date', '<=', datetime.today()), ('state', '=', 'approve')])
        for line in bonus_lines:
            if line.contract_id:
                emp_dict = self.get_employee_data(line)
                if line.new_job_id != self.job_id:
                    line.employee_id.write(emp_dict)
                    line.employee_bonus_id.write(emp_dict)
                contract_dict = self.get_contract_data(line)
                line.contract_id.write(contract_dict)
                line.state = 'done'
                if template_id:
                    template_id.send_mail(line.id, force_send=True, raise_exception=False)

    def action_button_done(self):
        """
            sent the status of generating record his/her bonus in 'done' state
        """
        self.ensure_one()
        try:
            template_id = self.env.ref('saudi_hr_bonus.hr_bonus_contract_updation_email')
        except ValueError:
            template_id = False
        if self.effective_date <= datetime.today().date():
            if self.contract_id:
                emp_dict = self.get_employee_data(self)
                if self.new_job_id != self.job_id:
                    self.employee_id.write(emp_dict)
                    self.employee_bonus_id.write(emp_dict)
                contract_dict = self.get_contract_data(self)
                self.contract_id.write(contract_dict)
                self.state = 'done'
            if template_id:
                template_id.send_mail(self.id, force_send=True, raise_exception=False)
        else:
            raise ValidationError(_('You Can not Done the Bonus Line Because Effective Date is %s.') % self.effective_date)

    def send_mail(self):
        """
            sent an email for salary promotion
        """
        self.ensure_one()
        context = self.env.context
        template_id = False
        for line in self:
            if line.is_increase:
                try:
                    template_id = self.env.ref('saudi_hr_bonus.email_template_salary_promotion')
                except ValueError:
                    template_id = False
            else:
                try:
                    template_id = self.env.ref('saudi_hr_bonus.email_template_salary_no_promotion')
                except ValueError:
                    template_id = False
        try:
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form')
        except ValueError:
            compose_form_id = False
        ctx = context.copy()
        ctx.update({'default_model': 'employee.bonus.lines',
                    'default_res_id': self.ids[0],
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id.id,
                    'default_composition_mode': 'comment',
                    })
        return {'name': _('Compose Email'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id.id, 'form')],
                'view_id': compose_form_id.id,
                'target': 'new',
                'context': ctx,
                }

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            bonus_id = self.env['employee.bonus'].browse(values.get('employee_bonus_id'))
            if bonus_id:
                values.update({'employee_id': bonus_id.employee_id.id,
                               'job_id': bonus_id.job_id.id,
                               })
            if values.get('employee_id', False) and values.get('fiscalyear_id', False):
                emp = self.env['hr.employee'].browse(values.get('employee_id'))
                fiscalyear_id = self.env['year.year'].browse(values.get('fiscalyear_id'))
                contract_ids = emp._get_contracts(fiscalyear_id.date_start, fiscalyear_id.date_stop, states=['open'])
                if contract_ids:
                    wage_amt = contract_ids[0].wage
                    values.update({'wage': wage_amt, 'contract_id': contract_ids[0].id})
            if values.get('wage', False) and values.get('wage', False) > 0:
                wage = values.get('wage')
                if values.get('proposed_hike', False):
                    proposed_amount = (wage + (wage * values.get('proposed_hike')) / 100)
                    values.update({'proposed_amount': proposed_amount})
                if values.get('accepted_hike', False):
                    accepted_amount = (wage + (wage * values.get('accepted_hike')) / 100)
                    values.update({'accepted_amount': accepted_amount})
                if values.get('bonus', False):
                    bonus_perc = ((values.get('bonus', False) * 100) / wage)
                    values.update({'bonus_percentage': bonus_perc})
        return super(EmployeeBonusLines, self).create(vals_list)

    def write(self, values):
        """
            Update an existing record.
            :param values: updated values
            :return: Current update record ID
        """
        for rec in self:
            bonus_id = self.env['employee.bonus'].browse(values.get('employee_bonus_id'))
            if bonus_id:
                values.update({'employee_id': bonus_id.employee_id.id,
                               'job_id': bonus_id.job_id.id,
                               })
            if values.get('employee_id', False) and values.get('fiscalyear_id', False):
                emp = self.env['hr.employee'].browse(values.get('employee_id'))
                fiscalyear_id = self.env['year.year'].browse(values.get('fiscalyear_id'))
                contract_ids = emp._get_contracts(fiscalyear_id.date_start, fiscalyear_id.date_stop, states=['open'])
                if contract_ids:
                    wage_amt = contract_ids[0].wage
                    values.update({'wage': wage_amt, 'contract_id': contract_ids[0].id})
            if values.get('wage', False) and values.get('wage', False) > 0:
                wage = values.get('wage', False)
            else:
                wage = rec.wage
            if values.get('proposed_hike', False):
                proposed_amount = (wage + (wage * values.get('proposed_hike')) / 100)
                values.update({'proposed_amount': proposed_amount})
            if values.get('accepted_hike', False):
                accepted_amount = (wage + (wage * values.get('accepted_hike')) / 100)
                values.update({'accepted_amount': accepted_amount})
            if values.get('bonus', False):
                bonus_perc = ((values.get('bonus', False) * 100) / wage)
                values.update({'bonus_percentage': bonus_perc})
        return super(EmployeeBonusLines, self).write(values)

    def unlink(self):
        """
            To remove the record, which is not in 'done' states
        """
        for line in self:
            if line.state in ['done']:
                raise UserError(_('You cannot remove the record which is in %s state!') % line.state)
        return super(EmployeeBonusLines, self).unlink()
