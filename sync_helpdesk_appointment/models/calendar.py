# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Meeting(models.Model):
    _inherit = 'calendar.event'

    def count_ticket(self):
        """
            Compute ticket
        """
        for rec in self:
            rec.ticket_count = len(rec.ticket_id) if rec.ticket_id else 0

    ticket_id = fields.Many2one('ticket.ticket', string="Ticket", copy=False)
    appointment_type = fields.Selection([('onsite', 'Onsite'), ('our_office', 'Our Office'), ('phone', 'Phone Call'), ('remote_support', 'Remote Support')], string="Appointment Type", copy=False)
    ticket_count = fields.Integer(string="Orders", compute=count_ticket)

    def show_ticket(self):
        """
            Show ticket related to Appointment
        """
        self.ensure_one()
        form_view = self.env.ref('sync_helpdesk.support_ticket_view_form')
        return {
            'name': 'Ticket',
            'view_mode': 'form',
            'res_model': 'ticket.ticket',
            'views': [(form_view.id, 'form')],
            'res_id' : self.ticket_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True
        }

    @api.onchange('appointment_type')
    def onchange_appointment_type(self):
        self.location = ''
        address = ''
        if self.appointment_type == 'onsite' and self.ticket_id.partner_id:
            if self.ticket_id.partner_id.street:
                address = self.ticket_id.partner_id.street + ','
            if self.ticket_id.partner_id.street2:
                address = address + self.ticket_id.partner_id.street2 + ','
            if self.ticket_id.partner_id.city:
                address = address + self.ticket_id.partner_id.city + ','
            if self.ticket_id.partner_id.zip:
                address = address + self.ticket_id.partner_id.zip
            if self.ticket_id.partner_id.country_id.name:
                address = address + self.ticket_id.partner_id.country_id.name
        elif self.appointment_type == 'our_office' and self.user_id:
            if self.user_id.company_id.street:
                address = self.user_id.company_id.street + ','
            if self.user_id.company_id.street2:
                address = address + self.user_id.company_id.street2 + ','
            if self.user_id.company_id.city:
                address = address + self.user_id.company_id.city + ','
            if self.user_id.company_id.zip:
                address = address + self.user_id.company_id.zip
            if self.user_id.company_id.country_id.name:
                address = address + self.user_id.company_id.country_id.name
        self.location = address

    def default_get_partner(self, user_id):
        if user_id:
            user_id = self.env['res.users'].browse(user_id)
            return user_id.partner_id.id
        return False
