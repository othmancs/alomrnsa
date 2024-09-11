# -*- coding: utf-8 -*-
# Part of Synconics. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class TicketReport(models.Model):
    """ Ticket Report"""
    _inherit="ticket.report"

    lead_id = fields.Many2one('crm.lead', string="Lead")

    def _select(self):
        return super(TicketReport, self)._select() + ", s.lead_id"

    def _group_by(self):
        return super(TicketReport, self)._group_by() + ", s.lead_id"
