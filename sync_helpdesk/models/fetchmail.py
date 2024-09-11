# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    is_ticket = fields.Boolean('Is Ticket')
    team_id = fields.Many2one('ticket.team', string="Ticket Team")

    @api.onchange('object_id')
    def object_onchange(self):
        """
            create method for the set ticket flag
        """
        self.is_ticket = False
        if self.object_id.model == 'ticket.ticket':
            self.is_ticket = True

    @api.model_create_multi
    def create(self, vals_list):
        """
            Override method for add email in ticket team
        """
        resources = super(FetchmailServer, self).create(vals_list)
        for res in resources:
            if res.is_ticket and res.team_id:
                # active_id = self.env['ticket.team'].browse(self.env.context.get('active_id'))
                # if active_id:
                res.team_id.username = res.user
        return resources

    def write(self, values):
        """
            Override method for add email in ticket team
        """
        for rec in self:
            if values.get('user'):
                rec.team_id.username = values['user']
        return super(FetchmailServer, self).write(values)
