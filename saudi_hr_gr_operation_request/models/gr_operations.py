# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class GrRequestType(models.Model):
    _name = 'gr.request.type'
    _description = 'GR Request type'
    _order = 'id desc'

    name = fields.Char(string='Name', required=True)
    documents = fields.Text(string='Documents', type="html")
    expense_needed = fields.Boolean(string='Expense Needed')


class GrOperations(models.Model):
    _name = 'gr.operations'
    _order = 'id desc'
    _inherit = 'hr.expense.payment'
    _description = 'GR Operations'

    def _expense_total(self):
        """
            In total expense calculate employee contribution.
        """
        for contribution in self:
            contribution.expense_total = contribution.emp_contribution + contribution.company_contribution

    name = fields.Char('Name')
    type_id = fields.Many2one('gr.request.type', required=True, string='Operation')
    expense_needed = fields.Boolean('Expense Needed')
    documents = fields.Text('List of Documents Required', readonly=True, default="")
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=lambda self: self.env['hr.employee'].get_employee())
    department_id = fields.Many2one('hr.department', string='Department')
    expense_total = fields.Float(compute=_expense_total, string='Total Expense', digits='Account')
    description = fields.Text('Description')
    is_damage = fields.Boolean('Damage')
    total = fields.Float('Total')
    state = fields.Selection([('draft', 'New'),
                              ('confirm', 'Waiting for Approval'),
                              ('inprogress', 'In progress'),
                              ('done', 'Done'),
                              ('refuse', 'Refuse')], string='Status', default='draft', tracking=True)
    approved_date = fields.Datetime('Approved Date', readonly=True, copy=False)
    approved_by = fields.Many2one('res.users', string='Approved by', readonly=True, copy=False)
    refused_by = fields.Many2one('res.users', string='Refused by', readonly=True, copy=False)
    refused_date = fields.Datetime('Refused on', readonly=True, copy=False)
    client_name = fields.Char('Client Name', size=50)
    project_name = fields.Char('Project Name', size=50)
    handled_by = fields.Many2one('hr.employee', string="Handled by")
    expense_ids = fields.Many2many('hr.expense', string="Expenses", copy=False)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.user.company_id)

    def _track_subtype(self, init_values):
        """
            Give the subtypes triggered by the changes on the record according
            to values that have been updated.
        """
        self.ensure_one()
        if 'state' in init_values and self.state == 'draft':
            return self.env.ref('saudi_hr_gr_operation_request.mt_gr_operations_new')
        elif 'state' in init_values and self.state == 'confirm':
            return self.env.ref('saudi_hr_gr_operation_request.mt_gr_operations_confirm')
        elif 'state' in init_values and self.state == 'done':
            return self.env.ref('saudi_hr_gr_operation_request.mt_gr_operations_done')
        elif 'state' in init_values and self.state == 'refuse':
            return self.env.ref('saudi_hr_gr_operation_request.mt_gr_operations_refuse')
        return super(GrOperations, self)._track_subtype(init_values)

    def unlink(self):
        """
            Delete/ remove selected record
            :return: Deleted record ID
        """
        for objects in self:
            if objects.state in ['confirm', 'inprogress', 'done', 'refuse']:
                raise UserError(_('You cannot remove the record which is in %s state!') % objects.state)
        return super(GrOperations, self).unlink()

    @api.depends('employee_id', 'type_id')
    def name_get(self):
        """
            to use retrieving the name, combination of `employee name & operation type name`
        """
        result = []
        for operation in self:
            name = ''.join([operation.employee_id.name or '', ' - ', operation.type_id.name or ''])
            result.append((operation.id, name))
        return result

    def _add_followers(self):
        """
            Add employee and gr add in followers
        """
        gr_groups_config_ids = self.env['hr.groups.configuration'].sudo().search([('branch_id', '=', self.employee_id.branch_id.id), ('gr_ids', '!=', False)])
        partner_ids = gr_groups_config_ids and [employee.user_id.partner_id.id for employee in gr_groups_config_ids.sudo().gr_ids if employee.user_id] or []
        if self.employee_id.user_id:
            partner_ids.append(self.employee_id.user_id.partner_id.id)
        if self.handled_by.user_id:
            partner_ids.append(self.handled_by.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner_ids)

    def submit_gr_operations(self):
        """
            sent the status of generating GR operation request in Confirm state
        """
        self.ensure_one()
        self.state = 'confirm'

    def set_to_draft(self):
        """
            sent the status of generating GR operation request in Set to Draft state
        """
        self.ensure_one()
        self.approved_by = False
        self.approved_date = False
        self.refused_by = False
        self.refused_date = False
        self.state = 'draft'

    def inprogress_gr_operations(self):
        """
            sent the status of generating GR operation request is In progress state
        """
        self.ensure_one()
        self.write({'state': 'inprogress',
                    'approved_by': self.env.uid,
                    'approved_date': datetime.today()})

    def refuse_gr_operations(self):
        """
            sent the status of generating GR operation request in Refuse state
        """
        self.ensure_one()
        return self.write({'state': 'refuse',
                           'refused_by': self.env.uid,
                           'refused_date': datetime.today()})

    def received_gr_operations(self):
        """
            sent the status of generating GR operation request in Done state
        """
        self.ensure_one()
        self.state = 'done'

    @api.onchange('type_id')
    def onchange_type(self):
        """
            Set credit according to request type.
        """
        self.documents = self.type_id.documents
        self.expense_needed = self.type_id.expense_needed
        self.expense_total = 0
        self.company_contribution = 0
        self.emp_contribution = 0

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            onchange the value based on selected employee
            job, department and company
        """
        self.department_id = False
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id
            self.company_id = self.employee_id.company_id.id

    def generate_expense(self):
        """
            Generate employee expense according to operation request
            return: created expense ID
        """
        self.ensure_one()
        product_id = self.env.ref('saudi_hr_gr_operation_request.operation_request')
        name = 'GR Operation - ' + self.name_get()[0][1]
        description = 'GR Operation - ' + self.name_get()[0][1]
        return self.generate_expense_payment(self, self.description, self.emp_contribution, self.company_contribution,
                                             self.payment_mode, name, product_id, self.expense_total)

    def view_expense(self):
        """
            Redirect to open expense method.
        """
        for line in self:
            return self.redirect_to_expense(line.expense_ids)
