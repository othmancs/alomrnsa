# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class Lead(models.Model):
    _inherit = "crm.lead"
    _description = "crm lead"

    def count_tickets(self):
        """
            Count tickets
        """
        for rec in self:
            rec.ticket_count = len(rec.ticket_ids) if rec.ticket_ids else 0

    ticket_count = fields.Integer(string="Tickets", compute=count_tickets)
    ticket_ids = fields.One2many('ticket.ticket', 'lead_id', string="Tickets")

    def action_view_tickets(self):
        """
            Show tickets
        """
        self.ensure_one()
        partner_obj = self.env['res.partner']
        context = dict(self.env.context)
        partner = self.partner_id
        if not partner:
            partner = partner_obj.search([('email', '=', self.email_from)])
            if not partner:
                partner = partner_obj.create({
                        'name': self.contact_name,
                        'title': self.title.id,
                        'function': self.function,
                        'phone': self.phone,
                        'email': self.email_from,
                        'mobile': self.mobile,
                        'street': self.street,
                        'street2': self.street2,
                        'city': self.city,
                        'state_id': self.state_id.id,
                        'zip': self.zip,
                        'country_id': self.country_id.id,
                        'website': self.website,
                        'type': 'contact'
                    })
        for rec in partner:
            context.update({
                'default_partner_id': rec.id,
                'partner_email': rec.email,
                'default_lead_id': self.id,
                'default_name': self.name,
                'default_medium_id': self.env.ref('sync_helpdesk_lead.utm_medium_lead').id
            })
        tree_view = self.env.ref('sync_helpdesk.support_ticket_view_tree')
        form_view = self.env.ref('sync_helpdesk.support_ticket_view_form')
        return {
            'name': 'Tickets',
            'view_mode': 'form',
            'res_model': 'ticket.ticket',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', 'in', self.ticket_ids.ids)],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True
        }
