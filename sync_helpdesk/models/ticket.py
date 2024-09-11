# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo.exceptions import UserError
from odoo import api, fields, models, _


class Ticket(models.Model):
    _name = 'ticket.ticket'
    _order = "ticket_no desc"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin', 'portal.mixin']
    _description = "Ticket"
    _rec_name = "ticket_no"

    @api.model
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        categ = self.env['ticket.category'].search([('is_default_queue', '=', True)])
        stage_id = categ.stage_ids
        if not stage_id:
            stage_id = self.env['ticket.stage'].search([], order='sequence', limit=1)
        if stage_id:
            return stage_id[0].id
        return False

    @api.model
    def _default_team_methods(self):
        """
            Create method for set default team
        """
        team_id = self.env['ticket.team'].search([('company_id', '=', self.env.user.company_id.id), ('member_ids', 'in', [self.env.uid])], order='running_tickets asc', limit=1)
        if team_id:
            return team_id.id
        return False

    @api.model
    def _default_medium(self):
        """
            Create method for set default medium
        """
        direct_medium_id = self.env.ref('utm.utm_medium_direct')
        if direct_medium_id:
            return direct_medium_id.id
        return False

    def _ticket_count(self):
        """
            Create method for count tickets
        """
        for ticket in self:
            count_tickets = self.search([('partner_id', '=', ticket.partner_id.id), ('id', '!=', ticket.id)])
            ticket.ticket_count = len(count_tickets)

    is_done = fields.Boolean('Done', help="Consider as a Ticket as a done.", copy=False)
    is_cancel = fields.Boolean("Is Cancel", copy=False)
    is_close = fields.Boolean(related='stage_id.is_close', string="Is Close")
    dont_email = fields.Boolean(string="Don't Email", default=False, tracking=True, copy=False)
    work_approved = fields.Boolean(string="Is work approved to proceed?", default=False, copy=False)
    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the ticket without removing it.")
    ticket_count = fields.Integer(compute='_ticket_count', string='#Ticket', copy=False)
    color = fields.Integer('Color Index')
    estimated_cost = fields.Float('Estimated Cost', copy=False)
    ticket_no = fields.Char('Reference', copy=False, readonly=True, default=lambda x: _('New'), help="Ticket Number.")
    name = fields.Char('Subject', required=True, tracking=True)
    partner_name = fields.Char('Name', invisible=True)
    partner_phone = fields.Char('Phone')
    partner_mobile = fields.Char('Mobile')
    partner_email = fields.Char('Email')
    description = fields.Text('Description')
    deadline = fields.Datetime('Deadline', copy=False)
    date = fields.Datetime('Created', default=fields.Datetime.now, copy=False, required=True)
    last_change_state_date = fields.Datetime('Last Stage Change', help="Show last change state date.", readonly=True, copy=False)
    stage_change_by = fields.Many2one('res.users', string="Stage Change By", readonly=True, copy=False)
    priority = fields.Selection([('0', 'All'), ('1', 'Low Priority'), ('2', 'High Priority'), ('3', 'Urgent')], 'Priority', default='0', copy=False)
    kanban_state = fields.Selection([('normal', 'Normal'), ('blocked', 'Blocked'), ('done', 'Ready for next stage')], string="Kanban State", default='normal', help="Kanban state.", copy=False)
    template_id = fields.Many2one('ticket.mail.template', string='Automated Answer Email Template')
    team_id = fields.Many2one('ticket.team', string='Assign Team', tracking=True, default=_default_team_methods)
    user_id = fields.Many2one('res.users', string='Assigned to', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
            default=lambda self: self.env.user.company_id)
    partner_id = fields.Many2one('res.partner', string="Customer", tracking=True)
    stage_id = fields.Many2one('ticket.stage', 'Stage', domain="[('categ_ids','=', categ_id)]", tracking=True, default=_get_default_stage_id, group_expand='_read_group_stage_ids', copy=False)
    categ_id = fields.Many2one('ticket.category', 'Ticket Type', required=True, default=lambda self: self.env['ticket.category'].search([('is_default_queue', '=', True)]), help="Queue Type.")
    medium_id = fields.Many2one('utm.medium', string='Origin', default=_default_medium,
                                help="This is the method of delivery.Ex: Postcard, Email, or Banner Ad")
    tag_ids = fields.Many2many('ticket.tag', string='Tags', tracking=True)
    work_location_id = fields.Many2one('res.partner', string='Employee Location')
    department_id = fields.Many2one('hr.department', string='Department')
    attachments = fields.Many2many('ir.attachment', string='Attachments')
    customer_ticket_histories = fields.Many2many('ticket.ticket', string='Ticket Histories', compute='compute_customer_ticket_histories')
    parent_ticket_id = fields.Many2one('ticket.ticket', string='Linked Ticket')
    stock_quants = fields.Many2many('stock.quant', string='Quants', compute='compute_stock_quants')

    def action_rmm(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://demo.tacticalrmm.com/',
            'target': 'new',
            # 'res_id': self.id,
        }

    def compute_stock_quants(self):
        stock_quant = self.env['stock.quant']
        for rec in self:
            stock_quants = [(5,)]
            user = rec.partner_id.user_ids
            if user and user[0].employee_id:
                equipments = user[0].employee_id.equipment_ids.mapped('product_id')
                quants = stock_quant.search([('product_id', 'in', equipments.ids), ('on_hand', '=', True), ('owner_id', '=', rec.partner_id.id)])
                stock_quants.append((6, 0, quants.ids))
            rec.stock_quants = stock_quants

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        type_id = self._context.get('default_categ_id')
        if type_id:
            tickets = self.env['ticket.ticket'].search([('team_id', '=', type_id)])
            type_ids = tickets.mapped('categ_id')
            if type_ids:
                return type_ids.stage_ids
        return self.env['ticket.stage'].search([])

    def compute_customer_ticket_histories(self):
        for rec in self:
            previous_tickets = rec.search([('id', '!=', rec.id),
                                        ('partner_id', '=', rec.partner_id.id)])
            rec.customer_ticket_histories = [(6, 0, previous_tickets.ids)]

    # @api.onchange('partner_id')
    # def onchange_partner_id

    def unlink(self):
        """
            Override method for restrict delete of ticket
        """
        for ticket in self:
            if ticket.is_done or ticket.is_cancel:
                raise UserError(_('You can not delete a ticket which are in done or cancel stage!'))
        return super(Ticket, self).unlink()

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        """
            Create method for set team
        """
        if self.categ_id.team_ids:
            team_id = self.env['ticket.team'].search([('id', 'in', self.categ_id.team_ids.ids), ('company_id', '=', self.env.user.company_id.id)], order='running_tickets asc', limit=1)
            self.team_id = team_id.id

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        """
            Create method for set automated email template
        """
        if self.stage_id:
            template_ids = self.stage_id.template_ids.filtered(lambda l: l.default)
            self.template_id = template_ids[0].id if template_ids else False

    def partner_ticket_count(self):
        """
            Show Same partner Count Ticket.
        """
        self.ensure_one()
        count_tickets = self.search([('partner_id', '=', self.partner_id.id), ('id', '!=', self.id)])
        form_view = self.env.ref('sync_helpdesk.support_ticket_view_form')
        tree_view = self.env.ref('sync_helpdesk.support_ticket_view_tree')
        return {
            'name': 'Ticket Number',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ticket.ticket',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', 'in', count_tickets.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True
        }

    def assign_ticket_to_self(self):
        """
            Create method for assign ticket to self
        """
        if not self.env.user.support_team_id or (self.team_id and self.env.user.support_team_id and self.env.uid not in self.team_id.member_ids.ids):
            raise UserError(_('You are not a team member, so you can not take this ticket!'))
        self.user_id = self.env.user.id

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
            Set partner name and email according to partner id.
        """
        self.partner_name = self.partner_id.name or ''
        self.partner_email = self.partner_id.email or ''
        self.partner_mobile = self.partner_id.mobile or ''
        self.partner_phone = self.partner_id.phone or ''
        user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id), ('employee_id', '!=', False)])
        if user:
            self.work_location_id = user.employee_id.work_location_id.id
            self.department_id = user.employee_id.department_id.id

    @api.model
    def create(self, vals):
        """
            Override method for the change state, add followers
        """
        context = dict(self.env.context)
        if 'fetchmail_cron_running' in context and 'default_fetchmail_server_id' in context:
            fetchmail_server = self.env['fetchmail.server'].browse(context['default_fetchmail_server_id'])
            if fetchmail_server.object_id and fetchmail_server.object_id.model == 'ticket.ticket':
                vals['name'] = vals['ticket_no']
                vals['ticket_no'] = False
        if not vals.get('ticket_no'):
            vals['ticket_no'] = self.env['ir.sequence'].next_by_code('ticket.ticket') or _('New')
        vals.update({'last_change_state_date': fields.Datetime.now(), 'stage_change_by': self.env.uid})
        if context.get('default_fetchmail_server_id'):
            mail_server_id = self.env['fetchmail.server'].browse(context.get('default_fetchmail_server_id'))
            medium = self.env.ref('utm.utm_medium_email')
            vals['medium_id'] = medium.id
            if mail_server_id.team_id:
                vals['team_id'] = mail_server_id.team_id.id
                vals['user_id'] = mail_server_id.team_id.user_id.id
        res = super(Ticket, self).create(vals)
        # ctx = self.env.context
        helpdesk_user_group = self.env.user.has_group('sync_helpdesk.group_helpdesk_user')
        helpdesk_manager_group = self.env.user.has_group('sync_helpdesk.group_helpdesk_manager')
        if helpdesk_user_group and not helpdesk_manager_group and res.user_id and res.user_id.id != self.env.uid:
            raise UserError(_('You can not assign ticket to other member!'))
        mail_sent = False
        if res.stage_id:
            res.is_done = True if res.stage_id.is_done else False
            res.is_cancel = True if res.stage_id.is_cancel else False
            if res.template_id.template_id and (res.partner_id and res.partner_id.email) and not res.dont_email:
                mail_sent = True
                res.template_id.template_id.with_context(subtype_id=self.env.ref('sync_helpdesk.mt_ticket_stage')).send_mail(res.id, force_send=True, raise_exception=False)
        assign_ticket_template = self.env.ref('sync_helpdesk.ticket_assignation_email')
        if (vals.get('user_id') or res.user_id) and assign_ticket_template and not mail_sent:
            assign_ticket_template.with_context(subtype_id=self.env.ref('sync_helpdesk.mt_ticket_stage')).send_mail(res.id, force_send=True, raise_exception=False)
        res.message_subscribe(partner_ids=res.partner_id.ids)
        company_ids = self.env['res.company'].search([])
        if res.partner_id and res.partner_id.country_id:
            company_id = company_ids.filtered(lambda l: l.partner_id.country_id == res.partner_id.country_id)
            if company_id:
                team_id = self.env['ticket.team'].search([('company_id', '=', company_id[0].id)],limit=1)
                res.team_id = team_id and team_id.id
        if res.team_id and res.team_id.company_id:
            res.company_id = res.team_id.company_id.id
        return res

    def write(self, vals):
        """
            Override method for the change state, add followers
        """
        if vals.get('user_id'):
            helpdesk_user_group = self.env.user.has_group('sync_helpdesk.group_helpdesk_user')
            helpdesk_manager_group = self.env.user.has_group('sync_helpdesk.group_helpdesk_manager')
            if helpdesk_user_group and not helpdesk_manager_group and vals['user_id'] != self.env.uid:
                raise UserError(_('You can not assign ticket to other member!'))
        if vals.get('stage_id'):
            template_id = False
            if vals.get('template_id'):
                template_id = self.env['ticket.mail.template'].browse(vals['template_id'])
            stage_id = self.env['ticket.stage'].browse(vals['stage_id'])
            vals.update({'last_change_state_date': fields.Datetime.now(), 'stage_change_by': self.env.uid, 'is_done': True if stage_id.is_done else False, 'is_cancel': True if stage_id.is_cancel else False})
            partner = self.env['res.partner'].browse(vals.get('partner_id', self.partner_id.id))
            dont_email = vals.get('dont_email', self.dont_email)
            if template_id and template_id.template_id and (partner and partner.email) and not dont_email:
                template_id.template_id.with_context(subtype_id=self.env.ref('sync_helpdesk.mt_ticket_stage')).send_mail(self.id, force_send=True, raise_exception=False)
        assign_ticket_template = self.env.ref('sync_helpdesk.ticket_assignation_email')
        if vals.get('user_id') and assign_ticket_template:
            assign_ticket_template.with_context(subtype_id=self.env.ref('sync_helpdesk.mt_ticket_stage')).send_mail(self.id, force_send=True, raise_exception=False)
        if vals.get('partner_id'):
            partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
            company_ids = self.env['res.company'].search([])
            if partner_id and partner_id.country_id:
                company_id = company_ids.filtered(lambda l: l.partner_id.country_id == partner_id.country_id)
                if company_id:
                    team_id = self.env['ticket.team'].search([('company_id', '=', company_id[0].id)],limit=1)
                    vals['team_id'] = team_id and team_id.id
            self.message_subscribe(partner_ids=[vals['partner_id']])
        if vals.get('team_id'):
            team_id = self.env['ticket.team'].browse(vals.get('team_id'))
            vals['company_id'] = team_id.company_id.id
        return super(Ticket, self).write(vals)

    @api.onchange('team_id')
    def onchange_team_id(self):
        """
            Create method for get recurring ticket
        """
        self.user_id = False
        for team in self.env['ticket.team'].search([]):
            team.get_running_ticket()
