# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class BaseAutomation(models.Model):
    _inherit = 'base.automation'

    @api.model
    def default_get(self, fields):
        """
            Override method for set default values
        """
        res = super(BaseAutomation, self).default_get(fields)
        context = dict(self.env.context)
        if context.get('for_ticket'):
            ticket_model_id = self.env['ir.model'].sudo().search([('model', '=', 'ticket.ticket')], limit=1)
            if ticket_model_id:
                res.update({'model_id': ticket_model_id.id})
            res.update({'state': 'object_write', 'trigger': 'on_write'})
        return res

    def default_followers(self, user_id):
        if user_id:
            return self.env['res.users'].browse(user_id).partner_id.id
        return False
