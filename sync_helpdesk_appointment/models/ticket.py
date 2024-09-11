# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class Ticket(models.Model):
    _inherit = 'ticket.ticket'

    def count_appointments(self):
        """
            Compute ticket appointments
        """
        for rec in self:
            rec.appointment_count = len(rec.appointment_ids) if rec.appointment_ids else 0

    appointment_count = fields.Integer(string="Orders", compute=count_appointments)
    appointment_ids = fields.One2many('calendar.event', 'ticket_id', string='Appointment', copy=False)

    def show_appointments(self):
        """
            Show all appointments related to ticket
        """
        self.ensure_one()
        context = dict(self.env.context)
        attendees = [self.env.user.partner_id.id]
        if self.partner_id:
            attendees.append(self.partner_id.id)
        if self.user_id:
            attendees.append(self.user_id.partner_id.id)
        context.update({'default_ticket_id':self.id, 'default_partner_ids':attendees, 'default_name': self.name})
        tree_view = self.env.ref('calendar.view_calendar_event_tree')
        form_view = self.env.ref('calendar.view_calendar_event_form')
        return {
            'name': 'Appointment',
            'view_mode': 'form',
            'res_model': 'calendar.event',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', 'in', self.appointment_ids.ids)],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True
        }
