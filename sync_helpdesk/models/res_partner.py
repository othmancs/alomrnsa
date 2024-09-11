# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = 'res.partner'

    def count_tickets(self):
        """
            Compute tickets
        """
        for rec in self:
            rec.ticket_count = len(rec.ticket_ids) if rec.ticket_ids else 0

    ticket_ids = fields.One2many('ticket.ticket', 'partner_id', string="Tickets")
    ticket_count = fields.Integer(string="# Ticket", compute='count_tickets')

    def action_view_tickets(self):
        """
            Create method for view tickets
        """
        if self.ticket_ids:
            action = self.env['ir.actions.actions']._for_xml_id('sync_helpdesk.support_ticket_action')
            if len(self.ticket_ids) > 1:
                action['domain'] = [('id', 'in', self.ticket_ids.ids)]
            elif len(self.ticket_ids) == 1:
                action['views'] = [(self.env.ref('sync_helpdesk.support_ticket_view_form').id, 'form')]
                action['res_id'] = self.ticket_ids.ids[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        context = dict(self.env.context)
        if 'is_ticket_partner' in context:
            users = self.env['res.users'].search([('employee_id', '!=', False)])
            args.append(('id', 'in', users.mapped('partner_id').ids))
        return super(Partner, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        domain = domain or []
        context = dict(self.env.context)
        if 'is_ticket_partner' in context:
            users = self.env['res.users'].search([('employee_id', '!=', False)])
            domain.append(('id', 'in', users.mapped('partner_id').ids))
        return super(Partner, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order, **read_kwargs)
