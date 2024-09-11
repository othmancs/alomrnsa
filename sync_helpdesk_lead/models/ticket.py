# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class Ticket(models.Model):
    _inherit = 'ticket.ticket'
    _description = 'Ticket'

    lead_id = fields.Many2one('crm.lead', string="Lead")
