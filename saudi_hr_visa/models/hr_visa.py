# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil import relativedelta as rdelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class HrVisa(models.Model):
    _name = 'hr.visa'
    _order = 'id desc'
    _inherit = 'hr.expense.payment'
    _rec_name = 'visa_ref'
    _description = "HR Visa"

    @api.depends('approved_date_from', 'approved_date_to')
    def period_of_stay(self):
        """
            Calculate employee visa duration.
        """
        for stay in self:
            if stay.approved_date_from and stay.approved_date_to:
                diff = rdelta.relativedelta(stay.approved_date_to, stay.approved_date_from)
                if diff.years > 0:
                    self.years = diff.years
                if diff.months > 0:
                    self.months = diff.months
                if diff.days > 0:
                    self.days = diff.days

    # Fields HR Visa
    visa_title = fields.Char(string='Visa Title', size=32)
    client_id = fields.Char(string='Client Name', size=50)
    reason_of_visa = fields.Selection([('annual_leave', 'Exit re-entry Visa'), ('final_exit', 'Final Exit'),
                                       ('renew_visa', 'Extension of Exit re-entry Visa')], string='Type of Visa', required=True)
    purpose_of_visa = fields.Selection([('training', 'Training'), ('business_trip', 'Business Trip'),
                                        ('annual_vacation', 'Annual Vacation'), ('holiday', 'Holiday'),
                                        ('secondment', 'Secondment'), ('emergency', 'Emergency'),
                                        ('other', 'Other'), ], string='Purpose of Visa', copy=False)
    ticket_type = fields.Selection([('single', 'Single'), ('multi', 'Multiple')], string='Type', default='single', copy=False)
    visa_for = fields.Selection([('individual', 'Individual'), ('family', 'Family'), ],
                                string='Visa For', required=True, default='individual', copy=False)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
                                  default=lambda self: self.env['hr.employee'].get_employee())
    name = fields.Char(string='name')
    country_id = fields.Many2one('res.country', string='Nationality', readonly=True)
    years = fields.Float(string='Visa Duration', compute='period_of_stay', store=True)
    months = fields.Float(compute='period_of_stay', store=True)
    days = fields.Float(compute='period_of_stay', store=True)
    email = fields.Char(string='Email')
    department_id = fields.Many2one('hr.department', readonly=True, string='Department')
    expense_total = fields.Float(string='Total Expense', digits='Account')
    expense_ids = fields.Many2many('hr.expense', string="Expenses", copy=False)
    requested_date_to = fields.Date(string='Return Date')
    requested_date_from = fields.Date(string='Departure Date', required=True)
    approved_date_to = fields.Date(string='Approved Date To')
    approved_date_from = fields.Date(string='Approved Date From')
    visa_ref = fields.Char(string='Visa Number')
    old_visa_ref = fields.Char(string='Old Visa Number')
    required_documents = fields.Text(string='List of Documents Required', readonly=True)
    description = fields.Text(string='Description')
    state = fields.Selection([('draft', 'To Submit'), ('confirm', 'Waiting Approval'), ('validate1', 'Approved'),
                              ('inprogress', 'In Progress'), ('received', 'Issued'),
                              ('refused', 'Refused')], string='State', default='draft')
    approved_date = fields.Datetime('Approved Date', readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved by', readonly=True)
    family_visa_ids = fields.One2many('employee.family.visa', 'visa_id', string='Family Details')
    handled_by = fields.Many2one('hr.employee', string='Handled by')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    def unlink(self):
        """
            Delete/ remove selected record
            :return: Deleted record ID
        """
        for objects in self:
            if objects.state in ['confirm', 'validate', 'validate1', 'inprogress', 'received', 'refused']:
                raise UserError(_('You cannot remove the record which is in %s state!') % objects.state)
        return super(HrVisa, self).unlink()

    @api.onchange('requested_date_from', 'requested_date_to')
    def _onchange_requested_date(self):
        """
            onchange the value based on requested date from and requested date to,
            raise validation error
        """
        for rec in self:
            if rec.requested_date_to and rec.requested_date_from and rec.requested_date_to < rec.requested_date_from:
                raise ValidationError(_('Departure Date must be greater then Return Date.'))

    @api.onchange('approved_date_to', 'approved_date_from')
    def _onchange_approve_date(self):
        """
            onchange the value based on approve date to and approve date from
            :raise validation error
        """
        for rec in self:
            if rec.approved_date_to and rec.approved_date_from and rec.approved_date_to < rec.approved_date_from:
                raise ValidationError(_('Approve Date to must be greater then Approve Date from.'))

    @api.depends('employee_id', 'approved_date_from', 'approved_date_to')
    def name_get(self):
        """
            to use retrieving the name, combination of `employee name, date from  & date to`
        """
        result = []
        for visa in self:
            if visa.approved_date_from and visa.approved_date_to:
                name = ''.join([visa.employee_id.name or '', '(', str(visa.approved_date_from) or '',
                                ' to ', str(visa.approved_date_to) or '', ')' or ''])
            else:
                name = visa.employee_id.name or ''
            result.append((visa.id, name))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('reason_of_visa', False):
                if values['reason_of_visa'] == 'final_exit':
                    values.update({'required_documents': """
                        1. Date of Ticket.
                        2. Clearance Letter from Bank.
                        3. Clearance Letter of Traffic Payment.
                        4. Clearance of Car.
                                        """})
                if values['reason_of_visa'] == 'annual_leave':
                    values.update({'required_documents': """
                        1. Valid IQAMA.
                        2. Valid Passport.
                        3. Clear Traffic Violence (If Any).
                                         """})
        return super(HrVisa, self).create(vals_list)

    def write(self, values):
        """
            Update an existing record
            :param values: current record fields data
            :return: updated record ID
        """
        if values.get('reason_of_visa', False):
            if values['reason_of_visa'] == 'final_exit':
                values.update({'required_documents': """
                    1. Date of Ticket.
                    2. Clearance Letter from Bank.
                    3. Clearance Letter of Traffic Payment.
                    4. Clearance of Car.
                                    """})
            if values['reason_of_visa'] == 'annual_leave':
                values.update({'required_documents': """
                    1. Valid IQAMA.
                    2. Valid Passport.
                    3. Clear Traffic Violence (If Any).
                                    """})
        return super(HrVisa, self).write(values)

    @api.constrains('requested_date_from', 'requested_date_to')
    def _check_request_dates(self):
        """
            Check request from and to date.
        """
        for contract in self.read(['requested_date_from', 'requested_date_to']):
            if contract['requested_date_from'] and contract['requested_date_to'] \
                    and contract['requested_date_from'] > contract['requested_date_to']:
                raise ValidationError(_('Error! Departure Date must be less than Return Date.'))

    @api.constrains('approved_date_from', 'approved_date_to')
    def _check_approved_dates(self):
        """
            Check approve from and to date.
        """
        for contract in self.read(['approved_date_from', 'approved_date_to']):
            if contract['approved_date_from'] and contract['approved_date_to'] \
                    and contract['approved_date_from'] > contract['approved_date_to']:
                raise ValidationError(_('Error! Approved Date From must be less than Approved Date To.'))

    def _add_followers(self):
        """
            Add employee and GR in followers
        """
        gr_groups_config_ids = self.env['hr.groups.configuration'].search([
            ('branch_id', '=', self.employee_id.branch_id.id), ('gr_ids', '!=', False)])
        partner_ids = gr_groups_config_ids and [employee.user_id.partner_id.id for employee in gr_groups_config_ids.sudo().gr_ids if employee.user_id] or []
        if self.employee_id.user_id:
            partner_ids.append(self.employee_id.user_id.partner_id.id)
        if self.employee_id.sudo().parent_id.user_id:
            partner_ids.append(self.employee_id.sudo().parent_id.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner_ids)

    def visa_confirm(self):
        """
            sent the status of generating visa his/her in reset to confirm state
        """
        self.ensure_one()
        self.state = 'confirm'

    def visa_validate1(self):
        """
            sent the status of generating visa his/her in reset to validate1 state
        """
        self.ensure_one()
        try:
            template_id = self.env.ref('saudi_hr_visa.email_template_visa_validate')
        except ValueError:
            template_id = False
        self.write({'state': 'validate1',
                    'approved_by': self.env.uid,
                    'approved_date': datetime.today()})
        create_date = datetime.strftime(self.create_date, DEFAULT_SERVER_DATE_FORMAT)
        if template_id:
            template_id.with_context({'create_date': create_date}).send_mail(self.id, force_send=True,
                                                                             raise_exception=False)
    def visa_inprogress(self):
        """
            sent the status of generating visa his/her in reset to inprogress state
        """
        self.ensure_one()
        self.state = 'inprogress'

    def visa_received(self):
        """
            sent the status of generating visa his/her in reset to receive state
        """
        self.ensure_one()
        if self.approved_date_from and self.visa_ref:
            try:
                template_id = self.env.ref('saudi_hr_visa.email_template_visa_received')
            except ValueError:
                template_id = False
            self.state = 'received'
            create_date = datetime.strftime(self.create_date, DEFAULT_SERVER_DATE_FORMAT)
            if template_id:
                template_id.with_context({'create_date': create_date}).send_mail(self.id, force_send=True,
                                                                                 raise_exception=False)
            if self.handled_by.user_id:
                self.message_subscribe(partner_ids=[self.handled_by.user_id.partner_id.id])
            self.message_post(message_type="email", body=_("Visa Request Received."))
        else:
            raise UserError(_('Please Enter Values For Visa Number, Approved Date From and Approved Date To'))

    def visa_refuse(self):
        """
            sent the status of generating visa his/her in reset to refuse state
        """
        self.ensure_one()
        self.state = 'refused'

    def set_draft(self):
        """
            sent the status of generating visa his/her in reset to draft state
        """
        self.ensure_one()
        self.write({'state': 'draft',
                    'approved_by': False,
                    'approved_date': False})

    @api.onchange('reason_of_visa')
    def onchange_reason_of_visa(self):
        """
            onchange the value based on selected reason of visa,
            required documents
        """
        document_list = ""
        if self.reason_of_visa:
            if self.reason_of_visa == 'final_exit':
                document_list = """
                    1. Date of Ticket.
                    2. Clearance Letter from Bank.
                    3. Clearance Letter of Traffic Payment.
                    4. Clearance of Car.
                                    """
            if self.reason_of_visa == 'annual_leave':
                document_list = """
                    1. Valid IQAMA.
                    2. Valid Passport.
                    3. Clear Traffic Violence (If Any).
                """
        self.required_documents = document_list

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            onchange the value based on selected employee of reason of visa,
            job, department, email
        """
        self.department_id = False
        self.country_id = False
        self.email = False
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id
            self.country_id = self.employee_id.sudo().country_id.id
            self.email = self.employee_id.work_email

    def generate_expense(self):
        """
            Generate employee expense according to operation request
            return: created expense ID
        """
        self.ensure_one()
        self.expense_total = self.emp_contribution + self.company_contribution
        product_id = self.env.ref('saudi_hr_visa.hr_visa_request')
        name = 'Visa -' + self.name_get()[0][1]
        return self.generate_expense_payment(self, self.description, self.emp_contribution, self.company_contribution,
                                             self.payment_mode, name, product_id, self.expense_total)

    def view_expense(self):
        """
            Redirect to employee expense method.
        """
        for line in self:
            return self.redirect_to_expense(line.expense_ids)


class EmployeeFamilyVisa(models.Model):
    _name = 'employee.family.visa'
    _order = 'id desc'
    _description = 'Employee Family Visa'

    visa_id = fields.Many2one('hr.visa', string='Visa')
    employee_id = fields.Many2one('hr.employee', related='visa_id.employee_id', string="Employee")
    member_name = fields.Char(string='Member Name (As in Passport)', required=True, size=128)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    birth_date = fields.Date(string='Date of Birth')
    relation = fields.Selection([('child', 'Child'), ('spouse', 'Spouse')], string='Relation')
    id_number = fields.Char(string='ID Number', size=20)
