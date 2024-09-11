# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.phone_validation.tools import phone_validation
from datetime import datetime as dt
from odoo.osv.expression import AND
import random


class HRWorkLocation(models.Model):
    _inherit = 'hr.work.location'

    def compute_total_employees(self):
        employee = self.env['hr.employee']
        for rec in self:
            rec.total_employees = employee.search_count([('work_location_id', '=', rec.id)])

    job_positions = fields.Many2many('hr.job', 'hr_work_location_job_rel', 'work_location_id', 'job_id', string='Job Positions')
    total_employees = fields.Integer(string='Total Employees', compute='compute_total_employees')
    company_number = fields.Char(related='company_id.company_number', string='Company Number')

    def action_view_total_employees(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employees',
            'res_model': 'hr.employee',
            'domain': [('work_location_id', '=', self.id)],
            'view_mode': 'tree',
            'target': 'current'
        }


class HrDepartment(models.Model):
    _inherit = 'hr.job'

    req_emp = fields.Integer('Required Employee', default=0)
    work_locations = fields.Many2many('hr.work.location', 'hr_work_location_job_rel', 'job_id', 'work_location_id', string='Work Locations')

    @api.constrains('name', 'department_id', 'company_id')
    def check_name(self):
        for rec in self:
            job_position = self.search([('name', '=', rec.name), ('department_id', '=', rec.department_id.id), ('company_id', '=', rec.company_id.id), ('id', '!=', rec.id)])
            if job_position:
                raise ValidationError(_('Name Should be unique!'))


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def get_current_contracts(self, date=fields.Date.today()):
        """
            get active contracts of employee
        """
        active_contract_ids = self.env['hr.contract'].search([
            ('state', 'not in', ['draft', 'close', 'cancel']),
            '&',
            ('employee_id', '=', self.id),
            '|',
            ('date_start', '<=', date),
            '|',
            ('date_end', '>=', date),
            ('date_end', '=', False),
            ])
        if active_contract_ids and len(active_contract_ids) > 1:
            raise UserError(_('Too many active contracts for employee %s') % self.name)
        return active_contract_ids

    @api.model
    def search_panel_select_range(self, field_name, **kwargs):
        field = self._fields[field_name]
        supported_types = ['many2one', 'selection']
        if field.type not in supported_types:
            types = dict(self.env["ir.model.fields"]._fields["ttype"]._description_selection(self.env))
            raise UserError(_(
                'Only types %(supported_types)s are supported for category (found type %(field_type)s)',
                supported_types=", ".join(types[t] for t in supported_types),
                field_type=types[field.type],
            ))

        model_domain = kwargs.get('search_domain', [])
        extra_domain = AND([
            kwargs.get('category_domain', []),
            kwargs.get('filter_domain', []),
        ])

        if field.type == 'selection':
            return {
                'parent_field': False,
                'values': self._search_panel_selection_range(field_name, model_domain=model_domain,
                                extra_domain=extra_domain, **kwargs
                            ),
            }

        Comodel = self.env[field.comodel_name].with_context(hierarchical_naming=False)
        field_names = ['display_name']
        hierarchize = kwargs.get('hierarchize', True)
        parent_name = False
        if hierarchize and Comodel._parent_name in Comodel._fields:
            parent_name = Comodel._parent_name
            field_names.append(parent_name)

            def get_parent_id(record):
                value = record[parent_name]
                return value and value[0]
        else:
            hierarchize = False

        comodel_domain = kwargs.get('comodel_domain', [])
        enable_counters = kwargs.get('enable_counters')
        expand = kwargs.get('expand')
        limit = kwargs.get('limit')

        if enable_counters or not expand:
            domain_image = self._search_panel_field_image(field_name,
                model_domain=model_domain, extra_domain=extra_domain,
                only_counters=expand,
                set_limit= limit and not (expand or hierarchize or comodel_domain), **kwargs
            )

        if not (expand or hierarchize or comodel_domain):
            values = list(domain_image.values())
            if limit and len(values) == limit:
                return {'error_msg': str(SEARCH_PANEL_ERROR_MESSAGE)}
            return {
                'parent_field': parent_name,
                'values': values,
            }

        if not expand:
            image_element_ids = list(domain_image.keys())
            if hierarchize:
                condition = [('id', 'parent_of', image_element_ids)]
            else:
                condition = [('id', 'in', image_element_ids)]
            comodel_domain = AND([comodel_domain, condition])
        if extra_domain and isinstance(extra_domain[0], tuple) and len(extra_domain[0]) > 0 and extra_domain[0][0] == 'company_id':
            comodel_domain += extra_domain
        comodel_records = Comodel.search_read(comodel_domain, field_names, limit=limit)

        if hierarchize:
            ids = [rec['id'] for rec in comodel_records] if expand else image_element_ids
            comodel_records = self._search_panel_sanitized_parent_hierarchy(comodel_records, parent_name, ids)

        if limit and len(comodel_records) == limit:
            return {'error_msg': str(SEARCH_PANEL_ERROR_MESSAGE)}

        field_range = {}
        for record in comodel_records:
            record_id = record['id']
            values = {
                'id': record_id,
                'display_name': record['display_name'],
            }
            if hierarchize:
                values[parent_name] = get_parent_id(record)
            if enable_counters:
                image_element = domain_image.get(record_id)
                values['__count'] = image_element['__count'] if image_element else 0
            field_range[record_id] = values

        if hierarchize and enable_counters:
            self._search_panel_global_counters(field_range, parent_name)

        return {
            'parent_field': parent_name,
            'values': list(field_range.values()),
        }

    def birthday_reminder(self):
        month = date.today().month
        day = date.today().day
        mail_channel_partner_obj = self.env['mail.channel.partner']
        odoobot = self.env.ref('base.partner_root')
        try:
            template_id = self.env.ref('saudi_hr.email_template_birthday')
        except ValueError:
            template_id = False
        for employee in self.search([('birthday', '!=', False), ('work_email', '!=', False)]):
            if employee.birthday.day == day and employee.birthday.month == month:
                if template_id:
                    template_id.send_mail(employee.id, force_send=True)

                if employee.user_id:
                    users = self.env['res.users'].search([
                        ('id', '!=', False),
                    ])
                else:
                    users = self.env['res.users'].search([])

                ("Hello,<br/>Your timesheet is remaining for last")
                message = _("Happy Birthday %s ! <br/> Many many happy returns of the day !") % employee.name
                if users:
                    for user in users:
                        if employee.user_id and employee.user_id.id == user.id:
                            continue
                        if employee.company_id.id not in user.company_ids.ids:
                            continue
                        channel = mail_channel_partner_obj.sudo().search([
                            ('partner_id','=',user.partner_id.id),
                            ('channel_id.channel_type','=','chat'),
                            ('channel_id.channel_partner_ids.id','=',user.partner_id.id),
                            ('channel_id.public','=','private')
                        ])
                        channel = channel.filtered(lambda x: len(x.channel_id.channel_partner_ids) == 1 and x.channel_id.is_chat == True and x.channel_id.member_count == 2)
                        if channel:
                            channel_send = channel.channel_id
                            if channel_send:
                                notification_ids = [(0, 0, {
                                    'res_partner_id': user.partner_id.id,
                                    'notification_type': 'inbox'
                                })]
                                channel_send.message_post(body=message, message_type="notification", subtype_xmlid="mail.mt_comment",
                                    author_id=odoobot.id,
                                    notification_ids=notification_ids)
                        else:
                            channel_send = self.env['mail.channel'].sudo().create({
                                'channel_partner_ids': [
                                    (4, user.partner_id.id),
                                ],
                                'is_chat': True,
                                'public': 'private',
                                'channel_type': 'chat',
                                'name': odoobot.name + ', '+ user.partner_id.name,
                            })
                            if channel_send:
                                notification_ids = [(0, 0, {
                                    'res_partner_id': user.partner_id.id,
                                    'notification_type': 'inbox'
                                })]
                                channel_send.message_post(body=message, message_type="notification", subtype_xmlid="mail.mt_comment", 
                                    author_id=odoobot.id,
                                    notification_ids=notification_ids)

    @api.depends('birthday')
    def _get_age(self):
        """
            Calculate age of Employee depends on Birth date.
        """
        for employee in self:
            if employee.sudo().birthday:
                employee.age = relativedelta(
                    fields.Date.from_string(fields.Date.today()),
                    fields.Date.from_string(employee.sudo().birthday)).years
            else:
                employee.age = 0

    @api.onchange('department_id')
    def _onchange_department(self):
        if self.department_id:
            self.job_id = False

    @api.depends('department_id')
    def _compute_parent_id(self):
        super(HrEmployee, self)._compute_parent_id()
        for employee in self.filtered('department_id.manager_id'):
            if employee.parent_id and not employee.parent_id.manager:
                employee.parent_id = False
            if employee.parent_id and not employee.parent_id.active:
                employee.parent_id = False

    @api.depends('parent_id')
    def _compute_coach(self):
        for rec in self:
            for employee in self.filtered('department_id.manager_id'):
                if employee.department_id.manager_id and employee.department_id.manager_id.is_hod:
                    employee.coach_id = employee.department_id.manager_id.id
                else:
                    employee.coach_id = False
                if employee.coach_id and not employee.coach_id.active:
                    employee.coach_id = False

    @api.constrains('birthday')
    def _check_birthday(self):
        """
            check the Employee age, eligible for doing a job or not.
            If Gender is male, He is age greater than 18.
            If Gender is female, She is age greater than 21.
        """
        for employee in self:
            if employee.birthday and employee.gender:
                diff = relativedelta(fields.date.today(), (employee.birthday))
                if employee.gender == "male" and abs(diff.years) < 18:
                    raise ValidationError(_("Male employee's age must be greater than 18"))
                elif employee.gender == 'female' and abs(diff.years) < 21:
                    raise ValidationError(_("Female Employee's age must be greater than 21."))

    @api.depends('date_of_join', 'date_of_leave')
    def _get_months(self):
        """
            Calculating Duration depends on `Date of Join`, `Date of Leave`
        """
        for employee in self:
            if employee.date_of_join:
                try:
                    join_date = datetime.strptime(str(employee.date_of_join), DEFAULT_SERVER_DATE_FORMAT)
                    to_date = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
                    current_date = datetime.strptime(str(to_date), DEFAULT_SERVER_DATE_FORMAT)
                    employee.duration_in_months = (current_date.year - join_date.year) * 12 + current_date.month - join_date.month
                except:
                    employee.duration_in_months = 0.0
            else:
                employee.duration_in_months = 0.0

    @api.model
    def get_employee(self):
        """
            Get Employee record depends on current user.
        """
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        return employee_ids[0] if employee_ids else False

    # ================Fields of HR employee=======================
    date_of_join = fields.Date('Joining Date', tracking=True)
    date_of_leave = fields.Date('Leaving Date')
    # ('active', 'Employment/Active'),
    #                                     ('inactive', 'Inactive'),
    #                                     ('long_term_secondment', 'Long Term Secondment'),
    #                                     ('probation', 'Probation'),
    #                                     ('notice_period', 'Notice Period'),
    #                                     ('terminate', 'Terminated/Inactive')
    employee_status = fields.Selection([('hired', 'Hired'),
                                        ('layoff', 'Layoff'),
                                        ('terminated', 'Terminated'),
                                        ('quit', 'Quit'),
                                        ('loa', 'LOA')
                                        ], string='Employment Status', default='hired', tracking=True)
    name = fields.Char(string='First Name')
    middle_name = fields.Char(size=64, string='Middle Name')
    last_name = fields.Char(size=64, string='Last Name')
    display_name = fields.Char(compute='_compute_display_name', recursive=True, store=True, index=True)
    code = fields.Char(string='Employee ID', readonly=False)
    age = fields.Float(compute='_get_age', compute_sudo=True, string="Age", store=False, readonly=True)
    sin_expiry_date = fields.Date(string='SIN Expiry')
    spouse_number = fields.Char('Spouse Phone Number', size=32)
    #branch_id = fields.Many2one('hr.branch', 'Office', tracking=True)
    duration_in_months = fields.Float(compute='_get_months', string='Month(s) in Organization')
    total_service_year = fields.Char(compute='_get_service_year', string="Total Service Year", compute_sudo=True)
    is_hod = fields.Boolean('Is HOD', help='Head of Department')
    manager = fields.Boolean(string='Is a Manager')
    profession = fields.Char(string='Profession')
    personal_access_token = fields.Char(string='Personal Access Token')
    nominee_id = fields.Many2one('res.partner', 'Name of Nominee', tracking=True)
    sponsored_by = fields.Selection([('company', 'Company'), ('other', 'Other')], string='Sponsored By',
                                    default=False)
    reference_by = fields.Char(string='Reference By')
    certificate_id = fields.Many2one('education.certificate', groups="hr.group_hr_user",
                                     tracking=True)
    study_id = fields.Many2one('education.study', groups="hr.group_hr_user", tracking=True)
    # study_name = fields.Char(string='Study')
    school_id = fields.Many2one('education.school', string='School.', groups="hr.group_hr_user", tracking=True)
    note = fields.Text('Note', copy=False)
    hr_id = fields.Many2one('hr.employee', string='HR', tracking=True)
    date_month = fields.Char(string='Date Month', compute='_get_date_month', store=True, readonly=True)
    # date_day = fields.Char(string='Date Month', compute='_get_date_month', store=True, readonly=True)

    # Add field for store data and using in Annual wage report
    service_year = fields.Float(string='Service Year', compute='_get_service_year', store='True', compute_sudo=True)
    employee_type = fields.Selection(selection_add=[('parttime', 'Part Time'), ('intern', 'Intern')], ondelete={'parttime': 'cascade', 'intern': 'cascade'})
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    is_benefits_enrolled = fields.Boolean(string='Benefits Enrolled')
    benefit_ref = fields.Char(string='Benefit ID')
    state_selection = fields.Selection([('done', 'Active'), ('non_active', 'Non Active')], default='done', string='State')
    second_job_id = fields.Many2one('hr.job', string='Second job Position')
    allergies_and_notable_health_conditions = fields.Text(string='Allergies and Notable Health Conditions')
    add_user_company_dir = fields.Boolean(string='Add User to Company Directory')
    is_visible_work_permit = fields.Boolean(string='Visible Permit', compute='compute_is_visible_work_permit')
    parking_type = fields.Selection([('onsite_parking', 'Requires On-site Parking'), ('outsite_parking', 'Does Not Requires On-site Parking')], default='outsite_parking', string='Parking')
    employee_personal_vehicle_id = fields.Many2one('ews.employee.personal.vehicle', string="Employee Personal Vehicle")
    ee_number = fields.Char(string='Make/Mode/Color')
    vehicle_number_plate = fields.Char(string='Plate', readonly=False)
    private_email = fields.Char(related=False, store=True)
    phone = fields.Char(related=False, store=True)
    country_code = fields.Char(related='country_id.code', string='Country Code')
    company_country_code = fields.Char(string='Company Country Code')

    @api.onchange('employee_personal_vehicle_id')
    def onchange_employee_personal_vehicle_id(self):
        if self.employee_personal_vehicle_id:
            self.ee_number = self.employee_personal_vehicle_id.ee_number
            self.vehicle_number_plate = self.employee_personal_vehicle_id.vehicle_number_plate

    _sql_constraints = [
        ('unique_emp_code', 'Check(1=1)', 'Employee Code must be unique!'),
    ]

    # _sql_constraints = []

    @api.depends('country_id', 'identification_id')
    def compute_is_visible_work_permit(self):
        for rec in self:
            rec.is_visible_work_permit = False
            if rec.country_code == 'CA' and rec.identification_id and rec.identification_id.startswith('9'):
                rec.is_visible_work_permit = True

    @api.depends('name', 'middle_name', 'last_name')
    def _compute_display_name(self):
        # diff = dict(show_address=None, show_address_only=None, show_email=None, html_format=None, show_vat=None)
        names = dict(self.name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    @api.onchange('state_selection')
    def onchange_state_selection(self):
        if self.state_selection == 'non_active':
            self.department_id = False
            self.parent_id = False
            self.coach_id = False

    def employee_enrollment(self):
        enrolled_months = self.env['ir.config_parameter'].sudo().get_param('saudi_hr.enrolled_months')
        if not enrolled_months:
            enrolled_months = 6
        joining_date = fields.Date.today() - relativedelta(months=enrolled_months)
        employees = self.sudo().search([('date_of_join', '!=', False), ('date_of_join', '<=', joining_date), ('is_benefits_enrolled', '=', False)])
        employees and employees.write({'is_benefits_enrolled': True})
        return True

    @api.onchange('work_phone', 'country_id', 'company_id')
    def _onchange_phone_validation(self):
        if self.work_phone:
            self.work_phone = self._phone_format(self.work_phone)

    @api.onchange('mobile_phone', 'country_id', 'company_id')
    def _onchange_mobile_validation(self):
        if self.mobile_phone:
            self.mobile_phone = self._phone_format(self.mobile_phone)

    @api.onchange('spouse_number', 'country_id', 'company_id')
    def _onchange_spouse_number(self):
        if self.spouse_number:
            self.spouse_number = self._phone_format(self.spouse_number)

    @api.onchange('emergency_phone', 'country_id', 'company_id')
    def _onchange_emergency_phone(self):
        if self.emergency_phone:
            self.emergency_phone = self._phone_format(self.emergency_phone)

    def _phone_format(self, number, country=None, company=None):
        country = country or self.country_id or self.env.company.country_id
        if not country:
            return number
        return phone_validation.phone_format(
            number,
            country.code if country else None,
            country.phone_code if country else None,
            force_format='INTERNATIONAL',
            raise_exception=False
        )

    def generate_link_for_private_info(self):
        template = self.env.ref('saudi_hr.mail_template_employee_manager_hr_evaluation')
        if template:
            number_random = random.randint(1200000000000000000, 3600000000000000000)
            url = '/employee/pinfo/%s' % number_random
            self.personal_access_token = number_random
            template.with_context({'access_token_url': url}).send_mail(self.id, force_send=True)
        return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Mail has been sent to the %s with link attached for filling the personal Information!' % self.display_name,
                    'sticky': False,
                    'type': 'success',
                }
            }

    @api.depends('birthday')
    def _get_date_month(self):
        for rec in self:
            if rec.birthday:
                rec.date_month = rec.birthday.strftime('%m')
                # rec.date_day = rec.birthday.strftime('%d')

    @api.model
    def default_get(self, fields_list):
        data = super(HrEmployee, self).default_get(fields_list)
        hr = self.env['ir.config_parameter'].sudo().get_param('saudi_hr.hr_id')
        if hr:
            data.update({'hr_id': int(hr)})
        return data

    @api.onchange('date_of_leave')
    def onchange_leave_date(self):
        """
            CHeck the Date of Leave must greater than Date of Join
        """
        if self.date_of_leave and self.date_of_join and self.date_of_leave < self.date_of_join:
            self.date_of_leave = False
            raise ValidationError(_("Leaving Date Must Be Greater Than Joining Date."))

    def _get_service_year(self):
        """
            Calculate the total no of years, total no of months.
        """
        for rec in self:
            if rec.date_of_join and rec.date_of_join < fields.date.today():
                if rec.date_of_leave:
                    diff = relativedelta((rec.date_of_leave), (rec.date_of_join))
                else:
                    diff = relativedelta(fields.date.today(), (rec.date_of_join))
                rec.service_year = diff.years
                rec.total_service_year = " ".join([str(diff.years), 'Years', str(diff.months), "Months"])
            else:
                rec.service_year = 0
                rec.total_service_year = "0 Years 0 Months"

    @api.depends('name', 'middle_name', 'last_name')
    def name_get(self):
        """
            Generate the single string for Name
            for eg. name: John, MiddleName: Pittu, LastName: Rank
            Calculated Name: John Pittu Rank
        """
        res = []
        for employee in self:
            name = employee.name
            name = ''.join([name or '', 
                ' %s' % employee.middle_name if employee.middle_name else '', 
                ' %s' % employee.last_name if employee.last_name else ''])
            res.append((employee.id, name))
        return res

    @api.model
    def age_notification(self):
        template_id = self.env.ref('saudi_hr.notification_employee_retirement', False)
        employees = []
        if template_id:
            for manager in self.env['hr.groups.configuration'].search([('hr_ids', '!=', False)]):
                for employee in self.env['hr.employee'].search([('branch_id', '=', manager.branch_id.id)]):
                    diff = relativedelta(datetime.today(), datetime.strptime(str(employee.birthday), DEFAULT_SERVER_DATE_FORMAT))
                    if diff and diff.years == 59 and diff.months == 6:
                        employees.append(employee.name)
                        if employee.code:
                            employees.append(employee.code)
                emp = ',\n'.join(employees)
                for hr in manager.hr_ids:
                    template_id.with_context(employees=emp).send_mail(hr.id, force_send=True, raise_exception=True)

    @api.model_create_multi
    def create(self, vals_list):
        employee_categ = self.env.ref('saudi_hr.saudi_hr_employee_category')
        for vals in vals_list:
            if 'category_ids' in vals:
                vals['category_ids'].append((4, employee_categ.id))
            else:
                vals['category_ids'] = [(4, employee_categ.id)]
            vals['code'] = self.env['ir.sequence'].next_by_code('hr.employee')
        return super(HrEmployee, self).create(vals_list)

    @api.onchange('company_id')
    def onchange_company(self):
        """
            set branch false
        """
        self.branch_id = False


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    department_number = fields.Char(string='Department Number')
