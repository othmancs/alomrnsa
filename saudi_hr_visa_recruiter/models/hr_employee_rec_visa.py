# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class HrEmployeeRecVisa(models.Model):
    _name = 'hr.employee.rec.visa'
    _order = 'id desc'
    _rec_name = 'visa_ref'
    _inherit = 'hr.expense.payment'
    _description = "HR Employee Visa requested by recruiter"

    def period_of_stay(self):
        """
            Calculate employee visa duration.
        """
        for stay in self:
            if stay.approved_date_from and stay.approved_date_to:
                timedelta = stay.approved_date_to - stay.approved_date_from
                diff = timedelta.days
                months = (diff / 30)
                stay.period_of_stay = months

    # Fields Hr Employee Rec Visa
    visa_title = fields.Char(string='Visa Title', size=32)
    reason_of_visa = fields.Selection([('business_visit_visa', 'Business Visit Visa'),
                                       ('commercial_visit_visa', 'Work Visit Visa'),
                                       ('new_join_employee', 'New Work Visa')], string='Type of Visa', required=True)
    visa_type = fields.Selection([('single', 'Single'), ('multi', 'Multiple')], string='Type', default='single')
    visa_for = fields.Selection([('individual', 'Individual'),
                                ('family', 'Family'), ], string='Visa For', required=True, default='individual')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    name = fields.Char(string='name')
    nationality = fields.Many2one('res.country', string='Nationality')
    period_of_stay = fields.Float(string='Visa Duration', compute=period_of_stay, store=True)
    email = fields.Char(string='Email')
    department_id = fields.Many2one('hr.department', readonly=True, string='Department')
    expense_total = fields.Float(string='Total Expense', digits='Account')
    expense_ids = fields.Many2many('hr.expense', string="Expenses", copy=False)
    requested_date_to = fields.Date(string='Return Date', required=False)
    requested_date_from = fields.Date(string='Departure Date', required=True)
    approved_date_to = fields.Date(string='Approved Date To')
    approved_date_from = fields.Date(string='Approved Date From')
    visa_ref = fields.Char(string='Visa Number')
    required_documents = fields.Text(string='List of Documents Required', readonly=True)
    description = fields.Text(string='Description')
    state = fields.Selection([('draft', 'To Submit'), ('confirm', 'Confirm'), ('inprogress', 'In Progress'),
                              ('received', 'Received'), ('refused', 'Refused')], 'State', default='draft', tracking=True)
    contact_person_ids = fields.One2many('res.partner', 'rec_user_id', string='Contact Person')
    family_visa_ids = fields.One2many('employee.rec.family.visa', 'visa_id', string='Family Details')
    request_by_id = fields.Many2one('hr.employee', string='Request by', required=True, default=lambda self: self.env['hr.employee'].get_employee())
    handled_by_id = fields.Many2one('hr.employee', string='Handled by')
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.user.company_id)

    def unlink(self):
        """
            Delete/ remove selected record
            :return: Deleted record ID
        """
        for objects in self:
            if objects.state in ['confirm', 'inprogress', 'received', 'refused']:
                raise UserError(_('You cannot remove the record which is in %s state!') % objects.state)
        return super(HrEmployeeRecVisa, self).unlink()

    @api.depends('employee_id', 'approved_date_from', 'approved_date_to')
    def name_get(self):
        """
            to use retrieving the name, combination of `employee name, date from and date to`
        """
        result = []
        for visa in self:
            if visa.approved_date_from and visa.approved_date_to:
                name = ''.join([visa.employee_id.name or '', '(', str(visa.approved_date_from) or '', ' to ', str(visa.approved_date_to) or '', ')' or ''])
            elif visa.approved_date_from:
                name = ''.join([visa.employee_id.name or '', '(', str(visa.approved_date_from) or '', ')' or ''])
            else:
                name = ''.join([visa.employee_id.name or ''])
            result.append((visa.id, name))
        return result

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            onchange the value based on selected employee,
            passport, job, department, nationality, email and company id
        """
        self.department_id = False
        self.nationality = False
        self.email = False
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id
            self.nationality = self.employee_id.sudo().country_id.id
            self.email = self.employee_id.work_email
            self.company_id = self.employee_id.company_id.id

    @api.constrains('requested_date_from', 'requested_date_to')
    def _check_request_dates(self):
        """
            Check request from date and request to date.
        """
        for contract in self.read(['requested_date_from', 'requested_date_to']):
            if contract['requested_date_from'] and contract['requested_date_to'] and contract['requested_date_from'] > contract['requested_date_to']:
                raise ValidationError(_('Error! Departure Date must be less than Return Date.'))

    @api.constrains('approved_date_from', 'approved_date_to')
    def _check_approved_dates(self):
        """
            Check approve from date and approve to date.
        """
        for contract in self.read(['approved_date_from', 'approved_date_to']):
            if contract['approved_date_from'] and contract['approved_date_to'] and contract['approved_date_from'] > contract['approved_date_to']:
                raise ValidationError(_('Error! Approved Date From must be less than Approved Date To.'))

    @api.onchange('reason_of_visa')
    def onchange_reason_of_visa(self):
        """
            onchange the value based on selected reason for visa,
            required document
        """
        document_list = ""
        if self.reason_of_visa:
            if self.reason_of_visa in ('business_visit_visa', 'commercial_visit_visa'):
                document_list = """
                                1. Date of Ticket
                                2. Clearance Letter of Traffic Payment
                                3. Clearance of Car
                              """
        self.required_documents = document_list

    def _add_followers(self, employee_ids=[]):
        """
            Add employee in followers
        """
        gr_groups_config_ids = self.env['hr.groups.configuration'].search([('branch_id', '=', self.employee_id.branch_id.id), ('gr_ids', '!=', False)])
        partner_ids = gr_groups_config_ids and [employee.user_id.partner_id.id for employee in gr_groups_config_ids.sudo().gr_ids if employee.user_id] or []
        for employee in employee_ids:
            if employee.user_id:
                partner_ids.append(employee.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner_ids)

    def visa_confirm(self):
        """
            sent the status of generating visa his/her in confirm state
        """
        self.ensure_one()
        followers = [self.employee_id, self.request_by_id]
        self._add_followers(followers)
        self.state = 'confirm'

    def visa_inprogress(self):
        """
            sent the status of generating visa his/her in inprogress state
        """
        self.ensure_one()
        if self.handled_by_id.user_id:
            self.message_subscribe(partner_ids=[self.handled_by_id.user_id.partner_id.id])
        self.state = 'inprogress'

    def visa_received(self):
        """
            sent the status of generating visa his/her in receive state
        """
        self.ensure_one()
        if self.approved_date_from and self.visa_ref:
            try:
                template_id = self.env.ref('saudi_hr_visa_recruiter.email_template_recruiter_visa_received')
            except ValueError:
                template_id = False
            create_date = datetime.strftime(self.create_date, DEFAULT_SERVER_DATE_FORMAT)
            if template_id:
                template_id.with_context({'create_date': create_date}).send_mail(self.id, force_send=True, raise_exception=False)
            self.state = 'received'
            self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_("Visa Request Received."))
        else:
            raise UserError(_('Please Enter Values For Visa Number, Approved Date From and Approved Date To'))

    def visa_refuse(self):
        """
            sent the status of generating visa his/her in refuse state
        """
        self.ensure_one()
        self.state = 'refused'
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_("Visa Request Refused."))

    def set_draft(self):
        """
            sent the status of generating visa his/her in draft state
        """
        self.ensure_one()
        self.state = 'draft'
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_("Visa Request Created."))

    def generate_expense(self):
        """
            Generate total expense of employee.
            return: created expense ID
        """
        self.ensure_one()
        self.expense_total = self.emp_contribution + self.company_contribution
        product_id = self.env.ref('saudi_hr_visa_recruiter.hr_visa_request')
        name = 'Visa -' + self.name_get()[0][1]
        return self.generate_expense_payment(self, self.description, self.emp_contribution, self.company_contribution, self.payment_mode, name, product_id, self.expense_total)

    def view_expense(self):
        """
            Redirect to show expense method.
            return: Current record expense ID
        """
        for line in self:
            return self.redirect_to_expense(line.expense_ids)


class EmployeeRecFamilyVisa(models.Model):
    _name = 'employee.rec.family.visa'
    _order = 'id desc'
    _description = 'Employee Family Visa'

    visa_id = fields.Many2one('hr.employee.rec.visa', string='Visa')
    employee_id = fields.Many2one('hr.employee', related='visa_id.employee_id', string='Employee')
    member_name = fields.Char(string='Member Name (As in Passport)', required=True, size=128)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    birth_date = fields.Date(string='Date of Birth')
    relation = fields.Selection([('child', 'Child'), ('spouse', 'Spouse')], string='Relation')
    id_number = fields.Char(string='ID Number', size=20)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'id desc'

    rec_user_id = fields.Many2one('hr.employee.rec.visa', string='partner')
