import datetime
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
from dateutil import relativedelta

date_format = "%Y-%m-%d"

class EmployeeGratuity(models.Model):
    _name = 'hr.gratuity'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Gratuity"

    # إضافة اختيار لتحديد تاريخ الحساب
    compute_at_date = fields.Selection([
        ('current_date', 'Current Date'),
        ('specific_date', 'At a Specific Date')
    ], string="Compute Gratuity At", default='current_date', help="Choose whether to compute gratuity for the current date or a specific date.")

    to_date = fields.Date("Gratuity Calculation Date", help="Choose a date to calculate gratuity at", default=fields.Date.today())

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validated'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled')],
        default='draft', tracking='onchange')
    
    name = fields.Char(string='Reference', required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.resignation', string='Employee',
                                  required=True, domain="[('state', '=', 'approved')]")
    joined_date = fields.Date(string="Joined Date", readonly=True)
    worked_years = fields.Integer(string="Total Work Years", readonly=True)
    last_month_salary = fields.Integer(string="Last Salary", required=True, default=0)
    allowance = fields.Char(string="Dearness Allowance", default=0)
    gratuity_amount = fields.Integer(string="Gratuity Payable", required=True,
                                     default=0, readonly=True, help=(
            "Gratuity is calculated based on the equation Last salary * Number of years of service * 15 / 26"))
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    # assigning the sequence for the record
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.gratuity')
        return super(EmployeeGratuity, self).create(vals)

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def check_request_existence(self):
        for rec in self:
            if rec.employee_id:
                gratuity_request = self.env['hr.gratuity'].search(
                    [('employee_id', '=', rec.employee_id.id),
                     ('state', 'in', ['draft', 'validate', 'approve', 'cancel'])])
                if gratuity_request:
                    raise ValidationError(_('A Settlement request is already processed for this employee'))

    def calculate_worked_years(self, to_date):
        """ حساب سنوات العمل بناءً على التاريخ المحدد """
        for rec in self:
            if rec.employee_id:
                # حساب الفرق بين تاريخ الانضمام والتاريخ المحدد
                diff = relativedelta.relativedelta(to_date, rec.joined_date)
                years = diff.years
                return years
        return 0

    def validate_function(self):
        # حساب سنوات العمل بناءً على التاريخ المحدد
        to_date = fields.Date.today() if self.compute_at_date == 'current_date' else self.to_date
        worked_years = self.calculate_worked_years(to_date)

        if worked_years < 1:
            self.write({'state': 'draft'})
            self.worked_years = worked_years
            raise exceptions.except_orm(
                _('Employee Working Period is less than 1 Year'),
                _('The employee is not eligible for gratuity with less than 1 year of service.'))

        else:
            self.worked_years = worked_years
            cr = self._cr

            query = """select amount from hr_payslip_line psl 
                       inner join hr_payslip ps on ps.id=psl.slip_id
                       where ps.employee_id=""" + str(self.employee_id.employee_id.id) + \
                    """and ps.state='done' and psl.code='NET'
                    order by ps.date_from desc limit 1"""

            cr.execute(query)
            data = cr.fetchall()
            if data:
                last_salary = data[0][0]
            else:
                last_salary = 0
            self.last_month_salary = last_salary

            if worked_years < 5:
                # No gratuity for less than 5 years
                self.gratuity_amount = 0
            elif 5 <= worked_years < 10:
                # Half a month salary for each year between 5 and 10 years
                self.gratuity_amount = (self.last_month_salary + int(self.allowance)) * worked_years * 0.5
            else:
                # One month salary for each year above 10 years
                self.gratuity_amount = (self.last_month_salary + int(self.allowance)) * worked_years

            self.gratuity_amount = round(self.gratuity_amount) if self.state == 'approve' else 0
            self.write({'state': 'validate'})

    def approve_function(self):
        if not self.allowance.isdigit():
            raise ValidationError(_('Allowance value should be numeric !!'))

        self.write({'state': 'approve'})

        amount = (self.last_month_salary + int(self.allowance)) * self.worked_years
        self.gratuity_amount = round(amount) if self.state == 'approve' else 0

    def cancel_function(self):
        self.write({'state': 'cancel'})

    def draft_function(self):
        self.write({'state': 'draft'})

    @api.onchange('employee_id')
    def _on_change_employee_id(self):
        rec = self.env['hr.resignation'].search([['id', '=', self.employee_id.id]])
        if rec:
            self.joined_date = rec.joined_date
        else:
            self.joined_date = ''
