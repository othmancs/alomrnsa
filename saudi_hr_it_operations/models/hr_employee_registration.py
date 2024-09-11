# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import time


class EquipmentRegistration(models.Model):
    _name = 'equipment.registration'
    _description = "Equipment Registration"
    _rec_name = 'item'

    reg_id = fields.Many2one('hr.employee.registration', 'IT Department')
    item = fields.Char('Item', required="True")
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Product Quantity')
    item_state = fields.Selection([('yes', 'YES'), ('no', 'NO'), ('na', 'N/A')], 'Status', required="True")
    category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category', required="True")
    handled_by = fields.Many2one('hr.employee', 'Handled by')
    remarks = fields.Char('Remarks')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        context = dict(self.env.context)
        args = args or []
        if 'default_employee_registraion_id' in context and isinstance(context['default_employee_registraion_id'], int):
            args.append(('reg_id', '=', context['default_employee_registraion_id']))
        return super(EquipmentRegistration, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        context = dict(self.env.context)
        domain = domain or []
        if 'default_employee_registraion_id' in context and isinstance(context['default_employee_registraion_id'], int):
            domain.append(('reg_id', '=', context['default_employee_registraion_id']))
        return super(EquipmentRegistration, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order, **read_kwargs)


class HRRegistration(models.Model):
    _name = 'hr.employee.registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Asset Registration"
    _rec_name = 'employee_name'

    @api.model
    def get_employee(self):
        """
            Get Employee record depends on current user.
        """
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        return employee_ids[0] if employee_ids else False

    @api.model
    def _get_equipment_registration(self):
        equipment_registration_lines = []
        equipment_registration_ids = self.env['equipment.registration'].search([('reg_id', '=', self.id)])
        for clearance_dept_id in equipment_registration_ids:
            equipment_registration_lines.append((0, 0, {'product_id': clearance_dept_id.product_id.id,
                                                        'item_state': clearance_dept_id.item_state,
                                                        'category_id': clearance_dept_id.category_id.id,
                                                        'item': clearance_dept_id.item
                                                        }))  # this dict contain keys which are fields of one2many field
        return equipment_registration_lines

    def unlink(self):
        """
            Remove record
        """
        for objects in self:
            if objects.state in ['confirm', 'receive', 'validate', 'approve', 'done', 'refuse']:
                raise UserError(_('You cannot remove the record which is in %s state!') % objects.state)
        return super(HRRegistration, self).unlink()

    # Fields HR Registration
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, domain="[('active', '=', True)]", default=get_employee)
    employee_name = fields.Char(string='Name', related='employee_id.name')
    handled_by = fields.Many2one('hr.employee', 'Handled by')
    department_id = fields.Many2one('hr.department', 'Department', readonly=True)
    registration_date = fields.Date('Registration Date', default=time.strftime('%Y-%m-%d'))
    email = fields.Char("Email")
    approved_date = fields.Datetime('Approved Date', readonly=True, copy=False)
    approved_by = fields.Many2one('res.users', 'Approved by', readonly=True, copy=False)
    validated_by = fields.Many2one('res.users', 'Validated by', readonly=True, copy=False)
    validated_date = fields.Datetime('Validated Date', readonly=True, copy=False)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting Approval'),
                              ('receive', 'Received'),
                              ('validate', 'Validated'),
                              ('approve', 'Approved'),
                              ('refuse', 'Refused'),
                              ('done', 'Done')], 'Status', default='draft', tracking=True)
    it_dept_ids = fields.One2many('equipment.registration', 'reg_id', 'IT Departments', default=_get_equipment_registration)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    picking_ids = fields.One2many('stock.picking', 'employee_registration_id', string='Pickings')
    total_pickings = fields.Integer(string='Total Pickings', compute='compute_total_pickings')
    employee_equipments_fields_ids = fields.One2many('employee.equipment.fields', 'employee_registration_id', string='Employee Equipments')


    def action_send_intake(self):
        equipment_list = []
        for equipment in self.employee_equipments_fields_ids:
            equipment_list.append((0, 0, {'equipment_registration_id': equipment.equipment_registration_id.id,
                                    'question_name': equipment.question_name}))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Equipment Required Details',
            'res_model': 'emp.equipment.fields.wizard',
            'context': {'default_employee_registraion_id': self.id, 'default_equipment_fields_line_wizard_ids': equipment_list},
            'target': 'new',
            'view_mode': 'form'
        }

    _sql_constraints = [
        ('employee_unique', 'unique(employee_id)', 'This employee Asset registration process is already done.'),
    ]

    def compute_total_pickings(self):
        for rec in self:
            rec.total_pickings = len(rec.picking_ids)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        """
            Department Details set based on Employee selection.
        """
        self.department_id = self.employee_id.department_id.id or False

    def _make_equipment_request(self, values):
        equipment_request_obj = self.env['maintenance.equipment.request']
        employee = values.get('employee_id', self.employee_id.id)
        for value in values.get('it_dept_ids'):
            if value[2] and value[2].get('item_state') == 'yes':
                equipment = {'category_id': value[2].get('category_id',),
                             'assign_to': 'employee', 'employee_id': employee,
                             'name': value[2].get('item')}
                equipment_request_obj.create(equipment)

    @api.model
    def create(self, values):
        """
            Create a new record
        """
        if values.get('employee_id'):
            employee = self.env['hr.employee'].browse(values['employee_id'])
            values.update({'department_id': employee.department_id.id or False})
        if values.get('it_dept_ids'):
            self._make_equipment_request(values)
        return super(HRRegistration, self).create(values)

    def write(self, values):
        """
            Update an existing record
        """
        if values.get('employee_id'):
            employee = self.env['hr.employee'].browse(values['employee_id'])
            values.update({'department_id': employee.department_id.id or False})
        return super(HRRegistration, self).write(values)

    def register_confirm(self):
        """
            set Registration of employee confirmed.
        """
        self.ensure_one()
        self.state = 'confirm'

    def register_receive(self):
        """
            Employee Received Registration.
        """
        self.ensure_one()
        self.state = 'receive'

    def register_validate(self):
        """
            Employee Asset Registration validate.
        """
        self.write({'state': 'validate',
                    'validated_by': self.env.uid,
                    'validated_date': fields.Datetime.now()})

    def register_approve(self):
        """
            Employee Asset Registration Approve.
        """
        picking_type_ids = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('company_id', '=', self.company_id.id),
                                                                '|', ('active', '=', True), ('active', '=', False)])
        picking_id = self.env['stock.picking']
        if not picking_type_ids:
            raise UserError(_('There is no Operation Types are defined for Internal Transfers!'))
        if not self.it_dept_ids:
            raise UserError(_('There is no any Equipments are defined to create Transfer!'))
        if not self.it_dept_ids.product_id:
            raise UserError(_('Product is not selected in Equipments!'))
        if not self.employee_id.user_id.partner_id:
            raise UserError(_('Employee must be a User to create transfer!'))
        if picking_type_ids and self.employee_id.user_id.partner_id and self.it_dept_ids and self.it_dept_ids.product_id:
            ctx = self._context.copy()
            ctx.update({'default_picking_type_id': picking_type_ids[0].id})
            location_dest_id = picking_type_ids[0].default_location_dest_id
            move_lines = []
            for line in self.it_dept_ids.filtered(lambda itid: itid.item_state == 'yes'):
                move_lines.append((0, 0, {'product_id': line.product_id.id,
                                        'product_uom_qty': line.product_qty,
                                        'name': line.product_id.display_name,
                                        'product_uom': line.product_id.uom_id.id,
                                        'location_id': picking_type_ids[0].default_location_src_id.id,
                                        'location_dest_id': location_dest_id.id}))
            if location_dest_id and move_lines:
                picking_id = picking_id.with_context(ctx).create({'partner_id': self.employee_id.user_id.partner_id.id,
                                    'location_dest_id': location_dest_id.id, 'picking_type_id': picking_type_ids[0].id,
                                    'employee_registration_id': self.id, 'move_ids_without_package': move_lines})
        self.ensure_one()
        self.write({'state': 'approve',
                    'approved_by': self.env.uid,
                    'approved_date': fields.Datetime.now()})
        if picking_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Equipments',
                'res_model': 'stock.picking',
                'res_id': picking_id.id,
                'view_mode': 'form',
                'target': 'current'
            }

    def register_cancel(self):
        """
            Employee Asset Registration cancel / refuse.
        """
        self.ensure_one()
        self.state = 'refuse'

    def register_done(self):
        """
            Employee Asset Registration done.
        """
        self.ensure_one()
        self.state = 'done'

    def set_to_draft(self):
        """
            Employee Asset Registration Reset to Draft or initial state.
        """
        self.ensure_one()
        self.state = 'draft'

    def action_view_pickings(self):
        return {'type': 'ir.actions.act_window',
                'name': 'Equipments',
                'res_model': 'stock.picking',
                'domain': [('employee_registration_id', '=', self.id)],
                'view_mode': 'tree,form',
                'target': 'current'}
