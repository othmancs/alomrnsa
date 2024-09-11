# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MaintenanceEquipmentRequest(models.Model):
    _name = 'maintenance.equipment.request'
    _inherit = 'hr.expense.payment'
    _order = "id desc"
    _description = 'Maintenance Equipment Request'

    @api.model
    def get_employee(self):
        """
            Get Employee record depends on current user.
        """
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        return employee_ids[0] if employee_ids else False

    name = fields.Char(string='Name', required=True)
    category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category', required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", default=get_employee)
    department_id = fields.Many2one('hr.department', string='Department')
    employee_department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Employee Department')
    employee_work_location_id = fields.Many2one('hr.work.location', related='employee_id.work_location_id', string='Employee Work Location')
    employee_company_id = fields.Many2one('res.company', related='employee_id.company_id', string='Employee Company')
    assign_to = fields.Selection([('department', 'Department'),
                                  ('employee', 'Employee'),
                                  ('other', 'Other')], string='Used By', required=True, default='employee')
    equipment_id = fields.Many2one('maintenance.equipment', string="Equipment")
    request_date = fields.Datetime(string="Request Date", default=fields.Datetime.now())
    return_date = fields.Datetime(string="Return Date")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Waiting for Approve'),
                              ('validate', 'Validated'), ('return', 'Returned'),
                              ('refuse', 'Refuse'), ('approve', 'Approve')],
                             string="Status", default="draft")
    emp_registration_id = fields.Many2one('hr.employee.registration', string='Employee Asset Registration')
    description = fields.Text(string='Description')
    # expense_id = fields.Many2one('hr.expense', 'Expense')
    expense_note = fields.Text('Expense Note')
    is_expense = fields.Boolean(string='Is Expense?')
    expense_total = fields.Float('Total Expense', digits=('Account'))
    # company_contribution = fields.Float('Company Contribution', digits=('Account'))
    # employee_contribution = fields.Float(compute=_employee_contribution, string='Employee Contribution', digits=('Account'))
    validated_date = fields.Datetime(string='Validated on', readonly=True, copy=False)
    validated_by = fields.Many2one('res.users', 'Validated by', readonly=True, copy=False)
    approved_date = fields.Datetime(string='Approved on', readonly=True, copy=False)
    approved_by = fields.Many2one('res.users', 'Approved by', readonly=True, copy=False)
    refused_by = fields.Many2one('res.users', 'Refused by', readonly=True, copy=False)
    refused_date = fields.Datetime(string='Refused on', readonly=True, copy=False)
    expense_ids = fields.Many2many('hr.expense', string="Expenses", copy=False)

    def unlink(self):
        """
            Remove a record
        """
        for equipment in self:
            if equipment.state in ['confirm', 'return', 'approve', 'refuse']:
                raise UserError(_('You cannot remove the record which is in %s state!') % equipment.state)
        return super(MaintenanceEquipmentRequest, self).unlink()

    def name_get(self):
        """
            Return a name with Concatinate Operation type and creation date
            for eg. Name + Equipment Type + Creation Date
        """
        res = []
        for equipment in self:
            # date = datetime.strptime(equipment.create_date, '%Y-%m-%d %H:%M:%S')
            name = ' - '.join([equipment.employee_id.name or '', equipment.category_id.name or '',
                               equipment.create_date.strftime('%Y-%m-%d') or ''])
            res.append((equipment.id, name))
        return res

    @api.onchange('assign_to')
    def onchange_used_by(self):
        """
            Onchange assign to
        """
        for equipment in self:
            if equipment.assign_to == 'department':
                equipment.employee_id = False
            elif equipment.assign_to == 'employee':
                equipment.department_id = False
            else:
                equipment.employee_id = False
                equipment.department_id = False

    def set_to_draft(self):
        """
            Set to draft of equipment
        """
        for equipment in self:
            equipment.state = 'draft'
            equipment.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Request Created.'))

    def action_equipment_refuse(self):
        """
            Refuse the state of equipment
        """
        for equipment in self:
            if equipment.state in ['approve', 'return']:
                raise UserError(_('Equiment Request is in %s state.') % equipment.state)
            equipment.state = 'refuse'
            equipment.refused_by = self.env.uid
            equipment.refused_date = fields.Datetime.now()
            equipment.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Request Refused.'))

    def action_equipment_return(self):
        """
            state return if equipment submitted
        """
        for equipment in self:
            equipment.state = 'return'
            equipment.return_date = fields.Datetime.now()
            equipment.equipment_id.employee_id = False
            equipment.equipment_id = False
            equipment.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Equipment Returned.'))

    def action_equipment_validate(self):
        """
            Validate IT Operation
        """
        self.ensure_one()
        helpdesk_groups_config_ids = self.env['hr.groups.configuration'].sudo().search([('branch_id', '=', self.employee_id.branch_id.id or False), ('helpdesk_ids', '!=', False)])
        partner_ids = helpdesk_groups_config_ids and [employee.user_id.partner_id.id for employee in helpdesk_groups_config_ids.helpdesk_ids if employee.user_id] or []
        self.message_subscribe(partner_ids=partner_ids)
        self.state = 'validate'
        self.validated_by = self.env.uid
        self.validated_date = fields.Datetime.now()
        self.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Request Validated.'))

    def action_equipment_approve(self):
        """
            Approve/give equipment by Used
        """
        for equipment in self:
            equipment.state = 'approve'
            equipment.approved_by = self.env.uid
            equipment.approved_date = fields.Datetime.now()
            equipment.equipment_id.employee_id = equipment.employee_id.id or False
            equipment.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Request Approved.'))

    def action_equipment_confirm(self):
        """
            Equipment state is confirmed
        """
        for equipment in self:
            equipment.state = 'confirm'
            if not equipment.request_date:
                equipment.request_date = fields.Datetime.now()
            equipment.message_post(message_type="email", subtype_xmlid='mail.mt_comment', body=_('Request Confirmed.'))

    def generate_expense(self):
        """
            Generate expense of employee.
            return: Generated expense ID
        """
        if self.expense_total <= 0 or self.company_contribution > self.expense_total:
            raise UserError(_('Expense Total should be either greater then 0 or company contribution should not be more that total expense'))
        self.ensure_one()
        product_id = self.env.ref('saudi_hr_it_operations.it_product')
        name = 'IT Operation - ' + self.name_get()[0][1]
        employee_id = self.employee_id
        if self.assign_to == 'department':
            if not self.department_id.manager_id:
                raise UserError(_('Please Assign Manager of %s') % self.department_id.name)
            employee_id = self.department_id.manager_id
        if self.assign_to == 'other' and not self.employee_id and not self.department_id:
            raise UserError(_('Please Select Employee or Department.'))
        return self.generate_expense_payment(self, self.description, self.emp_contribution, self.company_contribution, self.payment_mode, name, product_id, self.expense_total, employee_id=employee_id)

    def view_expense(self):
        """
            Redirect to view expense method.
            return: Current expense record ID
        """
        for line in self:
            return self.redirect_to_expense(line.expense_ids)
