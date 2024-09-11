# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MailTemplate(models.Model):
    _inherit = "mail.template"

    @api.model
    def default_get(self, fields):
        """
            Override method for set ticket model
        """
        res = super(MailTemplate, self).default_get(fields)
        context = dict(self.env.context)
        if context.get('for_ticket'):
            ticket_model_id = self.env['ir.model'].search([('model', '=', 'ticket.ticket')], limit=1)
            if ticket_model_id:
                res.update({'model_id': ticket_model_id.id})
        return res

    def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None, notif_layout=False):
        mail_id = super(MailTemplate, self).send_mail(res_id, force_send, raise_exception, email_values, notif_layout)
        mail = self.env['mail.mail'].browse(mail_id).exists()
        mail.update({'subtype_id': self._context['subtype_id'] if self._context.get('subtype_id') else {}})
        return mail_id
