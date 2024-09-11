# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, models, _


class Ticket(models.Model):
    _inherit = "ticket.ticket"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """
        Override method for hide action form the tree view
        """
        res = super(Ticket, self).get_view(view_id, view_type, **options)
        # if res.get('toolbar') and res.get('toolbar').get('action'):
        #     for action in res.get('toolbar').get('action'):
        #         if action.get('name') == 'Make Recurring' and view_type == 'tree':
        #             res.get('toolbar').get('action').remove(action)
        return res
