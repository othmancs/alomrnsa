# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError, ValidationError
from odoo.osv import expression


class HrCustody(models.Model):

    _name = 'hr.custody'
    _description = 'Hr Custody Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    read_only = fields.Boolean(string="check field")

    @api.onchange('employee')
    def _compute_read_only(self):
        """ Use this function to check weather the user has the permission to change the employee"""
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('nthub_hr_custody.group_custody_internal_transfer_user'):
            self.read_only = True
        else:
            self.read_only = False

    def mail_reminder(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([('state', '=', 'approved')])
        for i in match:
            if i.return_date:
                exp_date = fields.Date.from_string(i.return_date)
                if exp_date <= date_now:
                    base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                    url = base_url + _('/web#id=%s&view_type=form&model=hr.custody&menu_id=') % i.id
                    mail_content = _('Hi %s,<br>As per the %s you took custodies on %s for the reason of %s. S0 here we '
                                     'remind you that you have to return that on or before %s. Otherwise, you can '
                                     'renew the reference number(%s) by extending the return date through following '
                                     'link.<br> <div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
                                     'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
                                     'border-color:#875A7B;text-decoration: none; display: inline-block; '
                                     'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
                                     'cursor: pointer; white-space: nowrap; background-image: none; '
                                     'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
                                     'Renew %s</a></div>') % \
                                   (i.employee.name, i.name,i.date_request, i.purpose,
                                    date_now, i.name, url, i.name)
                    main_content = {
                        'subject': _('REMINDER On %s') % i.name,
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.employee.work_email,
                    }
                    mail_id = self.env['mail.mail'].create(main_content)
                    mail_id.mail_message_id.body = mail_content
                    mail_id.send()
                    if i.employee.user_id:
                        mail_id.mail_message_id.write({'partner_ids': [(4, i.employee.related_partner.id)]})


    def sent(self):
        self.state = 'to_approve'

    def send_mail(self):
        template = self.env.ref('nthub_hr_custody.custody_email_notification_template')
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.mail_send = True

    def set_to_draft(self):
        self.state = 'draft'



    def approve(self):
        self.activity_done()
        self.state = 'approved'


    def set_to_return(self):
        self.activity_done()
        self.state = 'returned'
        self.return_date = date.today()

    # return date validation
    @api.constrains('return_date')
    def validate_return_date(self):
        if self.return_date:
            if self.return_date < self.date_request:
                raise ValidationError(_('Please Give Valid Return Date'))

    approve_user = fields.Many2one('res.users')
    flag = fields.Boolean(compute = '_compute_state_after_validate')
    name = fields.Char(string='Code', copy=False, help="Code",default='New')
    company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id)
    rejected_reason = fields.Text(string='Rejected Reason', copy=False, readonly=True, help="Reason for the rejection")
    renew_rejected_reason = fields.Text(string='Renew Rejected Reason', copy=False, readonly=True,
                                        help="Renew rejected reason")
    date_request = fields.Date(string='Requested Date', required=True, track_visibility='always', readonly=True,
                               help="Requested date",
                               states={'draft': [('readonly', False)]}, default=datetime.now().strftime('%Y-%m-%d'))
    employee = fields.Many2one('hr.employee', string='Employee', required=True, readonly=True, help="Employee",
                               states={'draft': [('readonly', False)]},default=lambda self:self.env.user.employee_id)

    # hr_code = fields.Char(related='employee.hr_code',string='HR Code')
    purpose = fields.Char(string='Reason', track_visibility='always', required=True, readonly=True, help="Reason",
                          states={'draft': [('readonly', False)]})
    property_ids = fields.One2many('custody.property','custody', string='Property',
                                   help="Property name",
                                   states={'draft': [('readonly', False)]}
                                   )
    return_date = fields.Date(string='Return Date', required=False, track_visibility='always', readonly=True,
                              help="Return date",
                              states={'draft': [('readonly', False)]})
    renew_date = fields.Date(string='Renewal Return Date', track_visibility='always',
                             help="Return date for the renewal", readonly=True, copy=False)
    notes = fields.Html(string='Notes')
    renew_return_date = fields.Boolean(default=False, copy=False)
    renew_reject = fields.Boolean(default=False, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'Waiting Stock Validation'), ('approved', 'Done'),
                              ('to_approve_return','Partially Return'),('returned', 'Returned'), ('in_progress', 'In Progress'), ('rejected', 'Refused')], string='Status', default='draft',
                             track_visibility='always')
    mail_send = fields.Boolean(string="Mail Send")
    # analytic_account_id = fields.Many2one('account.analytic.account')
    project_id = fields.Many2one('project.project')
    custody_history_ids = fields.One2many('hr.custody.history','custody_id')

    stock_picking_type_id = fields.Many2one('stock.picking.type')
    it_picking_type_id = fields.Many2one('stock.picking.type')
    stock_location_id = fields.Many2one('stock.location')
    it_location_id = fields.Many2one('stock.location')
    destination_location_id = fields.Many2one('stock.location')
    source = fields.Selection([('it', 'IT'), ('stock', 'Inventory')])


    # @api.model
    # def _default_employee_id(self):
    #     return self._get_suid()


    def check_if_settings_set(self):
        param = self.env['ir.config_parameter'].sudo()
        location_dest_id = int(param.get_param('nthub_hr_custody.destination_location'))
        stock_location_id = int(param.get_param('nthub_hr_custody.stock_source_location'))
        stock_picking_type_id = int(param.get_param('nthub_hr_custody.stock_operation_type'))
        it_location_dest_id = int(param.get_param('nthub_hr_custody.it_source_location'))
        it_picking_type_id = int(param.get_param('nthub_hr_custody.it_operation_type'))
        if location_dest_id and stock_location_id and stock_picking_type_id and it_picking_type_id and it_location_dest_id:
            return location_dest_id,stock_location_id,stock_picking_type_id,it_location_dest_id,it_picking_type_id
        else:
            raise ValidationError('Please set employee locations settings from employee setting menu')
    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            location_dest_id, stock_location_id, stock_picking_type_id, it_location_id,\
            it_picking_type_id  = self.check_if_settings_set()
            self.destination_location_id = self.env['stock.location'].browse(location_dest_id)

            self.stock_location_id = self.env['stock.location'].browse(stock_location_id).id
            self.stock_picking_type_id = self.env['stock.picking.type'].browse(stock_picking_type_id).id

            self.it_location_id = self.env['stock.location'].browse(it_location_id).id
            self.it_picking_type_id = self.env['stock.picking.type'].browse(it_picking_type_id).id


    def create_stock_requisition(self):
        if any(line.source == 'stock' for line in self.property_ids):
            self.create_stock_order(self.stock_location_id.id,self.destination_location_id.id,self.stock_picking_type_id.id)
            self.state = 'to_approve'
            self.approve_user = self.env.user
        if any(line.source == 'it' for line in self.property_ids):
            self.create_it_order(self.it_location_id.id,self.destination_location_id.id,self.it_picking_type_id.id)
            self.state = 'to_approve'
            self.approve_user = self.env.user
        # else:
        #     raise ValidationError('Please chose source ("IT" or "STOCK") from lines')

    def create_stock_order(self,stock_location_id,stock_location_dest_id,stock_picking_type_id):
        stock_vals = {
            'partner_id': self.employee.related_partner.id,
            'picking_type_id': stock_picking_type_id,
            'location_id': stock_location_id,
            'location_dest_id': stock_location_dest_id,
            # 'analytic_account_id': self.employee.analytic_account_id.id,
            'project_id': self.employee.project_id.id,
            'origin': self.name,
            'custody_id': self.id,
        }

        stock_id = self.env['stock.picking'].sudo().create(stock_vals)
        for property in self.property_ids:
            if property.source == 'stock':
                stock_pick_vals = self._prepare_move_vals(line=property, picking_id=stock_id, location_id=stock_location_id, location_dest_id=stock_location_dest_id,
                                                          picking_type_id=stock_picking_type_id)
                self.env['stock.move'].sudo().create(stock_pick_vals)
        stock_id.send_activity()

    def create_it_order(self,it_location_id,it_location_dest_id,it_picking_type_id):
        it_vals = {
            'partner_id': self.employee.related_partner.id,
            'picking_type_id': it_picking_type_id,
            'location_id': it_location_id,
            'location_dest_id': it_location_dest_id,
            # 'analytic_account_id': self.employee.analytic_account_id.id,
            'project_id': self.employee.project_id.id,
            'origin': self.name,
            'custody_id': self.id,
        }

        it_id = self.env['stock.picking'].sudo().create(it_vals)
        for property in self.property_ids:
            if property.source == 'it':
                it_pick_vals = self._prepare_move_vals(line=property, picking_id=it_id, location_id=it_location_id, location_dest_id=it_location_dest_id,
                                                          picking_type_id=it_picking_type_id)
                self.env['stock.move'].sudo().create(it_pick_vals)
        it_id.send_activity()

    def create_return_stock_requisition(self):

        if any(line.source == 'stock' for line in self.property_ids):
            self.create_stock_order(self.destination_location_id.id,self.stock_location_id.id,self.stock_picking_type_id.id)
        if any(line.source == 'it' for line in self.property_ids):
            self.create_it_order(self.destination_location_id.id,self.it_location_id.id,self.it_picking_type_id.id)

        self.state = 'to_approve_return'
        self.approve_user = self.env.user
    def _prepare_move_vals(self, line=False, picking_id=False,location_id=False,location_dest_id=False,picking_type_id=False):
        pick_vals = {
            'product_id': line.product_id.id,
            'product_uom_qty': line.quantity,
            'product_uom': line.uom.id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            # 'analytic_account_id':self.analytic_account_id.id,
            'project_id':self.project_id.id,
            'name': 'RETURN'+str(line.product_id.name) if self.state == 'approved' else line.product_id.name,
            'picking_type_id': picking_type_id,
            'picking_id': picking_id.id,
        }
        return pick_vals
    def show_picking(self):
        for rec in self:
            res = self.env.ref('stock.action_picking_tree_all')
            res = res.read()[0]
            res['domain'] = str(['|',('custody_id', '=', rec.id),('origin','=','RETURN/ '+self.name)])
        return res

    def activity_done(self):
        activity_ids = self.env['mail.activity'].sudo().search([('res_id', '=', self.id)])
        if activity_ids:
            for act in activity_ids:
                act.action_done()

    def send_activity(self):
        user_id = self.approve_user.id
        now = fields.datetime.now()
        date_deadline = now.date()
        activ_list = []
        if user_id and user_id != 'None':
            activity_id = self.sudo().activity_schedule(
                'mail.mail_activity_data_todo', date_deadline,
                note=_(
                    '<a>Task </a> for <a>approve</a>') % (
                     ),
                user_id=user_id,
                res_id=self.id,

                summary=_("PLZ approve this custody for employee %s")% self.employee.name
            )
            activ_list.append(activity_id.id)
        [(4, 0, rec) for rec in activ_list]

    # method to calculate qty on hand for product over project and site and location


    @api.depends('property_ids')
    def _compute_state_after_validate(self):
        if not any(line.quantity != line.delivered for line in self.property_ids) and self.state == 'to_approve':
            self.approve()

        if not any(line.quantity != line.returned for line in self.property_ids) and self.state == 'to_approve_return':
            self.set_to_return()
        self.flag = False

    @api.onchange('employee')
    def onchange_employee_id(self):
        if self.employee and self.employee.project_id:
            self.project_id = self.employee.project_id
            self.add_history_line()
    def add_history_line(self):
        if self.custody_history_ids:
            self.custody_history_ids[-1].state = 'done'
            values = {
                'employee_id': self.employee.id,
                'date': fields.Date.today(),
                'state': 'active',
                'custody_id': self.id
            }
            self.env['hr.custody.history'].create(values)

    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.custody.seq')
        res = super(HrCustody, self).create(vals)
        values = {
        'employee_id' : vals.get('employee'),
        'date' : fields.Date.today(),
        'state' : 'active',
        'custody_id': res.id
        }
        self.env['hr.custody.history'].create(values)
        return res

class HrPropertyName(models.Model):
    """
            Hr property creation model.
            """
    _name = 'custody.property'
    _description = 'Property Name'

    custody = fields.Many2one('hr.custody')
    name = fields.Char(string='Property Name', required=True)
    image = fields.Image(string="Image",
                         help="This field holds the image used for this provider, limited to 1024x1024px")
    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image of this provider. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized image", attachment=True,
        help="Small-sized image of this provider. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    desc = fields.Html(string='Description', help="Description")
    company_id = fields.Many2one('res.company', 'Company', help="Company",
                                 default=lambda self: self.env.user.company_id)
    property_selection = fields.Selection([('empty', 'No Connection'),
                                           ('product', 'Products')],
                                          default='product',
                                          string='Property From', help="Select the property")

    product_id = fields.Many2one('product.product', string='Product', help="Product")
    serial_no = fields.Char()
    lot_id = fields.Many2one(
        'stock.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id)]",
        help="Lot/Serial Number of the product to unbuild.")
    source = fields.Selection(related='custody.source')
    quantity = fields.Integer(default=1)
    returned = fields.Integer()
    delivered = fields.Integer()
    qty_onhand = fields.Float(related="product_id.qty_available",readonly=True,string="Available QTY", store=True)
    uom = fields.Many2one('uom.uom', string=_('Unit of Measure'), required=True)
    # report_id = fields.Many2one('report.custody')
    job_id = fields.Many2one('hr.job')
    # available_product_ids = fields.Many2many('product.product', string='Product', compute='compute_product_project')
    project_id = fields.Many2one('project.project', related='custody.project_id', store=True)
    def _compute_read_only(self):
        """ Use this function to check weather the user has the permission to change the employee"""
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        print(res_user.has_group('nthub_hr_custody.group_custody_internal_transfer_user'))
        if res_user.has_group('nthub_hr_custody.group_custody_internal_transfer_user'):
            self.read_only = True
        else:
            self.read_only = False


    @api.onchange('product_id')
    def onchange_product(self):
        self.name = self.product_id.name
        self.uom = self.product_id.uom_id.id



    # @api.depends('custody.project_id')
    # def compute_product_project(self):
    #     for rec in self:
    #         rec.available_product_ids = self.env['stock.quant'].search([('project_id', '=', rec.custody.project_id.id)]).product_id
    #



    @api.onchange('product_id','source','project_id')
    def onchange_product_id(self):
        domain = []
        if self.source == 'it' and self.product_id:
            domain = [('product_id', '=', self.product_id.id), ('location_id', '=', self.custody.it_location_id.id)]
        elif self.source == 'stock' and self.product_id:
            domain = [('product_id', '=', self.product_id.id), ('location_id', '=', self.custody.stock_location_id.id)]

        # if self.custody.project_id:
        #     domain = expression.AND([[('project_id', '=', self.custody.project_id.id)], domain])

        stock_quant = self.env['stock.quant'].sudo().search(domain)
        if stock_quant:
            self.qty_onhand = sum(stock_quant.mapped('quantity'))
        else:
            self.qty_onhand = 0
        self.uom = self.product_id.uom_id.id

    @api.constrains('qty_onhand','quantity')
    def validate_quantity(self):
        for rec in self:
            if rec.qty_onhand < rec.quantity:
                raise ValidationError(_("You can't request more than in your warehouse  "))

