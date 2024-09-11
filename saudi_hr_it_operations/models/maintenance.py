# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import base64
import qrcode
import qrcode.image.svg
from odoo.exceptions import UserError
from io import BytesIO


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    branch_id = fields.Many2one('hr.branch', string='Office', )#default=lambda self: self.env.user.branch_id
    attachments = fields.Many2many('ir.attachment', 'attachment_id', 'maintenance_equipment_id', 'attachments_maintenance_equipment_rel', string='Attachments')
    product_id = fields.Many2one('product.product', string='Product')
    product_category_id = fields.Many2one('product.category', related='product_id.categ_id', string='Product Category')
    image = fields.Binary(string='Image', related='product_id.image_1920')
    qr_code_image = fields.Binary(string='QR Code Image', related='product_id.product_tmpl_id.qr_code_image')
    inspection_form_id = fields.Many2one('equipment.inspection.form', string='Inspection Form')
    inspection_schedule = fields.Selection(related='inspection_form_id.schedule_selection', string='Schedule')
    maintenance_equipment_histories = fields.Many2many('maintenance.request', string='Maintenance History', compute='compute_maintenance_equipment_histories')
    inspection_qr_code = fields.Char("QR Code", copy=False, compute='generate_inspection_qr_code')
    equipment_category_type = fields.Selection(related='category_id.equipment_category_type', string='Category Type')
    inspection_qr_code_image = fields.Binary(string='qr code image', store=True)
    submitted_inspections_ids = fields.One2many('equipment.submit.inspection', 'equipment_id', string='Inspections')
    system_cpu = fields.Char(string='CPU')
    system_ram = fields.Char(string='RAM')
    system_storage = fields.Char(string='Storage')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        context = dict(self.env.context)
        if 'check_shop_equipment' in context:
            categories = self.env['maintenance.equipment.category'].search([('equipment_category_type', '=', 'shop')])
            args.append(('category_id', 'in', categories.ids))
        return super(MaintenanceEquipment, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        domain = domain or []
        context = dict(self.env.context)
        if 'check_shop_equipment' in context:
            categories = self.env['maintenance.equipment.category'].search([('equipment_category_type', '=', 'shop')])
            domain.append(('category_id', 'in', categories.ids))
        return super(MaintenanceEquipment, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order, **read_kwargs)

    def create_repair_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Repair Order',
            'res_model': 'repair.order',
            'context': {
                'default_company_id': self.company_id.id,
                'default_product_id': self.product_id.id,
                'default_partner_id': self.employee_id.user_partner_id.id,
            },
            'view_mode': 'form',
            'target': 'current'
        }

    def generate_inspection_qr_code(self):
        def get_qr_encoding(tag, field):
            value = field.encode('UTF-8')
            tag = tag.to_bytes(length=1, byteorder='big')
            length = len(value).to_bytes(length=1, byteorder='big')
            return tag + length + value

        for rec in self:
            qr_code_str = ''
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            # action = self.env.ref('stock.product_template_action_product')
            # menu_id = self.env.ref('stock.menu_product_variant_config_stock')
            # /web#model=sale.order&id=8&action=345&view_type=form
            url = base_url + '/redirect_equipment_inspenction/%s' % self.id
            str_to_encode = get_qr_encoding(1, url)
            qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
            rec.inspection_qr_code = qr_code_str
            img = qrcode.make(url, image_factory=qrcode.image.svg.SvgImage)
            temp = BytesIO()
            img.save(temp)
            qr_img = base64.b64encode(temp.getvalue())
            rec.inspection_qr_code_image = qr_img

    @api.model
    def _read_group_category_ids(self, categories, domain, order):
        return categories

    def compute_maintenance_equipment_histories(self):
        for rec in self:
            requests = self.env['maintenance.request'].search([('equipment_id', '=', self._origin.id)])
            rec.maintenance_equipment_histories = [(6, 0, requests.ids)]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
            Override method for apply domain on user
        """
        context = dict(self.env.context)
        if context.get('category_id') and context.get('assign_to'):
            args.extend([('category_id', '=', context.get('category_id')),
                         ('equipment_assign_to', '=', context.get('assign_to'))])
            if context.get('assign_to') == 'employee':
                args.append(('employee_id', '=', False))
            elif context.get('assign_to') == 'department':
                args.append(('department_id', '=', False))
        return super(MaintenanceEquipment, self).name_search(name, args=args, operator=operator, limit=limit)

    @api.model
    def create(self, vals):
        res = super(MaintenanceEquipment, self).create(vals)
        res.open_product()
        return res

    def open_quants(self):
        self.open_product()
        res = self.product_id.action_open_quants()
        res['context']['default_owner_id'] = self.employee_id.user_partner_id.id
        return res

    def open_product(self):
        if not self.product_id:
            equipment_sequence = self.env['ir.sequence'].next_by_code('maintenance.equipment.reference')
            default_code = '%s%s' % (self.name[0:3], equipment_sequence)
            product = self.product_id.create({'name': self.name,
                                            'detailed_type': 'product',
                                            'is_equipment': True,
                                            'default_code': default_code,
                                            'equipment_company_id': self.company_id.id})
            self.product_id = product.id
        else:
            self.product_id.equipment_company_id = self.company_id.id
        return {'type': 'ir.actions.act_window',
                'name': 'Product',
                'res_model': 'product.product',
                'res_id': self.product_id.id,
                'view_mode': 'form',
                'target': 'current'}

    def open_run_inspection(self):
        inspection_lines = [(5,)]
        if not self.inspection_form_id:
            raise UserError(_('Inspection Form Is required to Proceed!'))
        for line in self.inspection_form_id.equipment_inspection_form_line_ids:
            inspection_lines.append((0, 0, {'name': line.name}))
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        if not employee:
            raise UserError(_('There is no any employee linked with current user!'))
        name = '%s-%s' % (self.inspection_form_id.name, fields.Date.today().strftime('%d%m%Y'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Run Inspection',
            'res_model': 'equipment.run.inspection',
            'context': {'default_equipment_form_id': self.inspection_form_id.id, 'default_name': name,'default_equipment_id': self.id, 'default_employee_id': employee[0].id, 'default_department_id': employee[0].department_id.id, 'default_run_inspenction_line_ids': inspection_lines},
            'view_mode': 'form',
            'target': 'current'
        }

    def open_submitted_inspection(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Submitted Inspection',
            'res_model': 'equipment.run.inspection',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('equipment_id', '=', self.id), ('state', '=', 'submitted')]
        }

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            team_ids = self.env['maintenance.team'].search([('branch_id', '=', self.branch_id.id)]).ids
            self.maintenance_team_id = False
            if len(team_ids) > 0:
                self.maintenance_team_id = team_ids[0]
            return {'domain': {'maintenance_team_id': [('id', 'in', team_ids)]}}
        else:
            return {'domain': {'maintenance_team_id': []}}

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     if self.company_id:
    #         branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
    #         self.branch_id = False
    #         if len(branches) > 0:
    #             self.branch_id = branches[0]
    #         return {'domain': {'branch_id': [('id', 'in', branches)]}}
    #     else:
    #         return {'domain': {'branch_id': []}}

    def _create_new_request(self, date):
        self.ensure_one()
        self.env['maintenance.request'].create({
            'name': _('Preventive Maintenance - %s') % self.name,
            'request_date': date,
            'schedule_date': date,
            'category_id': self.category_id.id,
            'equipment_id': self.id,
            'maintenance_type': 'preventive',
            'owner_user_id': self.owner_user_id.id,
            'user_id': self.technician_user_id.id,
            'maintenance_team_id': self.maintenance_team_id.id,
            'duration': self.maintenance_duration,
            'company_id': self.company_id.id or self.env.company.id,
            'branch_id': self.branch_id.id,
            })


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    branch_id = fields.Many2one('hr.branch', string='Office')#, default=lambda self: self.env.user.branch_id
    department_id = fields.Many2one('hr.department', string='Department')

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            team_ids = self.env['maintenance.team'].search([('branch_id', '=', self.branch_id.id)]).ids
            self.maintenance_team_id = False
            if len(team_ids) > 0:
                self.maintenance_team_id = team_ids[0]
            return {'domain': {'maintenance_team_id': [('id', 'in', team_ids)]}}
        else:
            return {'domain': {'maintenance_team_id': []}}

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     if self.company_id:
    #         branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
    #         self.branch_id = False
    #         if len(branches) > 0:
    #             self.branch_id = branches[0]
    #         return {'domain': {'branch_id': [('id', 'in', branches)]}}
    #     else:
    #         return {'domain': {'branch_id': []}}

    @api.onchange('equipment_id', 'company_id')
    def onchange_equipment_id(self):
        super(MaintenanceRequest, self).onchange_equipment_id()
        if self.equipment_id and self.equipment_id.branch_id:
            self.branch_id = self.equipment_id.branch_id.id


class MaintenanceTeam(models.Model):
    _inherit = 'maintenance.team'

    branch_id = fields.Many2one('hr.branch', string='Office')# , default=lambda self: self.env.user.branch_id

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     if self.company_id:
    #         branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
    #         self.branch_id = False
    #         if len(branches) > 0:
    #             self.branch_id = branches[0]
    #         return {'domain': {'branch_id': [('id', 'in', branches)]}}
    #     else:
    #         return {'domain': {'branch_id': []}}

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
            Override method for apply domain on user
        """
        args = args or []
        context = dict(self.env.context)
        if context.get('branch_id', False):
            args.append(('branch_id', '=', context.get('branch_id')))
        return super(MaintenanceTeam, self).name_search(name, args=args, operator=operator, limit=limit)
