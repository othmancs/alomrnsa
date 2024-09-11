# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, api, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    support_team_id = fields.Many2one(
        'ticket.team', 'Ticket Team',
        help='Ticket Team the user is member of. Used to compute the members of a ticket team through the inverse one2many')
    team_history_ids = fields.Many2many('ticket.team', 'user_team_rel', 'user_id', 'team_id', string="Teams")

    def write(self, vals):
        """
            Override method for add follower in ticket team
        """
        for user in self:
            if user.support_team_id and vals.get('support_team_id'):
                user.team_history_ids = [(4, user.support_team_id.id)]
        res = super(ResUsers, self).write(vals)
        for user in self:
            user.support_team_id.message_subscribe(partner_ids=user.partner_id.ids)
        return res

    def action_reset_password(self):
        context = dict(self.env.context)
        if 'create_user' in context and isinstance(context.get('create_user'), bool):
            return True
        return super(ResUsers, self).action_reset_password()

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        context = dict(self.env.context)
        if 'ticket_team_id' in context:
            team_id = self.env['ticket.team'].browse(context.get('ticket_team_id'))
            users = team_id.member_ids
            users |= team_id.user_id
            args.append(('id', 'in', users.ids))
        return super(ResUsers, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        domain = domain or []
        context = dict(self.env.context)
        if 'ticket_team_id' in context:
            team_id = self.env['ticket.team'].browse(context.get('ticket_team_id'))
            users = team_id.member_ids
            users |= team_id.user_id
            domain.append(('id', 'in', users.ids))
        return super(ResUsers, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order, **read_kwargs)
