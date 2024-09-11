# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TicketTag(models.Model):
    _name = "ticket.tag"
    _description = 'Ticket Tag'

    name = fields.Char('Name', required=True)
    color = fields.Integer('Color')


class TicketTeam(models.Model):
    _name = "ticket.team"
    _order = "sequence"
    _inherit = ['mail.thread']
    _description = "Ticket Team"

    def _assigned_tickets(self):
        """
            Compute assign tickets
        """
        for rec in self:
            assign_ticket = self.env['ticket.ticket'].search([('user_id','!=', False), ('team_id', '=', rec.id)])
            rec.assigned_tickets = len(assign_ticket)

    def _unassigned_tickets(self):
        """
            Compute unassign tickets
        """
        for rec in self:
            unassign_ticket = self.env['ticket.ticket'].search([('user_id','=', False), ('team_id', '=', rec.id)])
            rec.unassigned_tickets = len(unassign_ticket)

    def _ticket_count(self):
        """
            Compute tickets count
        """
        for rec in self:
            count_tickets = self.env['ticket.ticket'].search([('team_id','=',rec.id)])
            rec.ticket_count = len(count_tickets)

    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the technical team without removing it.")
    name = fields.Char('Ticket Team', required=True, translate=True)
    username = fields.Char('Email', readonly=True)
    sequence = fields.Integer(default=10)
    reply_to = fields.Char(string='Reply-To',
                           help="The email address put in the 'Reply-To' of all emails sent by ticket about cases in this technical team")
    ticket_count = fields.Integer(compute='_ticket_count', string='# Ticket')
    running_tickets = fields.Integer(string='Running Tickets')
    color = fields.Integer(string='Color Index', help="The color of the team")
    company_id = fields.Many2one('res.company', string='Company', required=True,
            default=lambda self: self.env.user.company_id)
    parent_id = fields.Many2one('ticket.team', string='Parent Team')
    user_id = fields.Many2one('res.users', string='Team Leader')
    # member_ids = fields.One2many('res.users', 'support_team_id', string='Team Members', copy=False)
    member_ids = fields.Many2many('res.users', string='Team Members', copy=False)
    unassigned_tickets = fields.Integer(compute='_unassigned_tickets', string='Unassigned Tickets', copy=False)
    assigned_tickets = fields.Integer(compute='_assigned_tickets', string='Assigned Tickets', copy=False)
    ticket_ids = fields.One2many('ticket.ticket', 'team_id', string="Tickets")
    show_dashboard = fields.Boolean('Show in Dashboard')
    show_in_hrms = fields.Boolean('Show in HRMS')
    show_in_maintenance = fields.Boolean('Show in Maintenance')

    @api.model
    def create(self, vals):
        """
            Override method for set team
        """
        if vals.get('user_id'):
            if 'member_ids' in vals and isinstance(vals.get('member_ids'), list):
                vals['member_ids'].append((4, vals.get('user_id')))
            else:
                # vals['member_ids']
                vals.update({'member_ids': [(4, vals.get('user_id'))]})
        return super(TicketTeam, self).create(vals)
        # res = super(TicketTeam, self).create(vals)
        # if vals.get('user_id'):
        #     res.user_id.support_team_id = res.id
        # return res

    def write(self, vals):
        """
            Override method for set team
        """
        for rec in self:
            if vals.get('user_id'):
                # user_id = self.env['res.users'].browse(vals['user_id'])
                # user_id.support_team_id = rec.id
                if 'member_ids' in vals and isinstance(vals.get('member_ids'), list):
                    vals['member_ids'].append((4, vals.get('user_id')))
                else:
                    # vals['member_ids']
                    vals.update({'member_ids': [(4, vals.get('user_id'))]})
        return super(TicketTeam, self).write(vals)

    def team_ticket_count(self):
        """
            Show same team count ticket.
        """
        self.ensure_one()
        count_tickets = self.env['ticket.ticket'].search([('team_id','=', self.id)])
        form_view = self.env.ref('sync_helpdesk.support_ticket_view_form')
        tree_view = self.env.ref('sync_helpdesk.support_ticket_view_tree')
        return {
            'name': 'Ticket Number',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ticket.ticket',
            'views': [(tree_view.id,'tree'), (form_view.id, 'form')],
            'domain': [('id', 'in', count_tickets.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True
        }

    def get_running_ticket(self):
        """
            Update recurring ticket on team
        """
        self.ensure_one()
        ticket_ids = self.env['ticket.ticket'].search([('team_id','=', self.id),('stage_id.is_close', '!=', True)])
        self.write({'running_tickets': len(ticket_ids.ids)})

    @api.constrains('parent_id')
    def _check_parent_team(self):
        """
            Check parent id constraint
        """
        self.ensure_one()
        if self.parent_id.id == self.id:
            raise UserError(_('You should not take recursive team.'))

    def create_incoming_mail_server(self):
        """
            Create incomming mail server for the ticket team
        """
        res = self.env.ref('fetchmail.view_email_server_form')
        ticket_model_id = self.env['ir.model'].search([('model', '=', 'ticket.ticket')])
        return   {
            'name': _('Incoming Mail Server'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res.id],
            'res_model': 'fetchmail.server',
            'context': "{'default_team_id':"+ str(self.id) +", 'default_object_id':"+ str(ticket_model_id.id) +"}",
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': False,
        }

    def unlink_incoming_mail_server(self):
        """
            Unlink mail server of ticket team
        """
        for rec in self:
            mail_server_id = self.env['fetchmail.server'].search([('team_id', '=', rec.id)])
            mail_server_id.unlink()
            rec.username = False

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
            Override method for apply domain
        """
        context = dict(self.env.context)
        if context.get('categ_id', False):
            categ_id = self.env['ticket.category'].browse(context['categ_id'])
            if categ_id.team_ids:
                args.append(('id', 'in', categ_id.team_ids.ids))
        return super(TicketTeam, self).name_search(name, args=args, operator=operator, limit=limit)


class TicketStages(models.Model):
    _name = "ticket.stage"
    _rec_name = 'name'
    _order = "sequence"
    _description = 'Ticket Stags'

    is_close = fields.Boolean('Closing Kanban Stags')
    is_done = fields.Boolean('Is Done')
    is_cancel = fields.Boolean("Is Cancel")
    fold = fields.Boolean('Folded' ,help='This stage is folded in the kanban view when there are no records in that stage to display.')
    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    color = fields.Integer('Color')
    template_ids = fields.One2many('ticket.mail.template', 'stage_id', string= 'Automated Answer Email Templates')
    categ_ids = fields.Many2many('ticket.category', 'queue_type_ticket_stage_rel', 'stage_id', 'categ_id', string='Ticket Type', help="Ticket types.")
    active = fields.Boolean(string='Active', default=True)


class TicketCategory(models.Model):
    _name = "ticket.category"
    _description = 'Ticket Category'
    _order = 'sequence'

    @api.constrains('is_default_queue')
    def _check_default_queue(self):
        """
            Check constraint for default queue.
        """
        default_queue_ids = self.search([('is_default_queue', '=', True)]).ids
        if len(default_queue_ids) > 1:
            raise UserError(_('Already one queue is as default queue!'))
        return True

    is_default_queue = fields.Boolean('Is Default Queue', help="Considered as a default queue.")
    active = fields.Boolean('Active', default=True)
    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('Code', required=True)
    color = fields.Integer('Color')
    stage_ids = fields.Many2many('ticket.stage', 'queue_type_ticket_stage_rel', 'categ_id', 'stage_id', string="Stages", help="Stages")
    team_ids = fields.Many2many('ticket.team', string='Team',
        help='Specific team that uses this stage. Other teams will not be able to see or use this stage.')
    default_team_id = fields.Many2one('ticket.team', string='Default Team')
    sequence = fields.Integer(string='Sequence')

    _sql_constraints = [
        ('code', 'unique(code)', 'Code must be unique!')
    ]


class TicketMailTemplate(models.Model):
    _name = "ticket.mail.template"
    _rec_name = 'template_id'
    _description = 'Ticket Mail Template'

    default = fields.Boolean(string="Default")
    template_id = fields.Many2one('mail.template', domain=[('model_id','=','ticket.ticket')], string= 'Automated Answer Email Template', required=True)
    stage_id = fields.Many2one('ticket.stage', string="Stage")
