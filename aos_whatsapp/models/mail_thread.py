# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models, _, api, fields

from odoo.tools import html2plaintext, plaintext2html

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    wa_template = fields.Boolean('Whatsapp Default')
    allowed_user_ids = fields.Many2many(
        comodel_name='res.users', string="Users",
        domain=[('share', '=', False)])

    @api.model
    def _find_default_for_model(self, model_name):
        return self.search([
            ('model', '=', model_name),
            ('wa_template', '=', True),
            '|',
                ('allowed_user_ids', '=', False),
                ('allowed_user_ids', 'in', self.env.user.ids)
        ], limit=1)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'
    
    def _notify_thread(self, message, msg_vals=False, **kwargs):
        recipients_data = super(MailThread, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
        # print ('--_notify_thread--',recipients_data,message,msg_vals)
        # print ('--kwargs--',kwargs)
        # self._notify_thread_by_whatsapp(message, recipients_data, msg_vals=msg_vals, **kwargs)
        return recipients_data

    def _notify_thread_by_whatsapp(self, message, recipients_data, msg_vals=False,
                              sms_numbers=None, sms_pid_to_number=None,
                              resend_existing=False, put_in_queue=False, **kwargs):
        """ Notification method: by SMS.

        :param message: ``mail.message`` record to notify;
        :param recipients_data: list of recipients information (based on res.partner
          records), formatted like
            [{'active': partner.active;
              'id': id of the res.partner being recipient to notify;
              'groups': res.group IDs if linked to a user;
              'notif': 'inbox', 'email', 'sms' (SMS App);
              'share': partner.partner_share;
              'type': 'customer', 'portal', 'user;'
             }, {...}].
          See ``MailThread._notify_get_recipients``;
        :param msg_vals: dictionary of values used to create the message. If given it
          may be used to access values related to ``message`` without accessing it
          directly. It lessens query count in some optimized use cases by avoiding
          access message content in db;

        :param sms_numbers: additional numbers to notify in addition to partners
          and classic recipients;
        :param pid_to_number: force a number to notify for a given partner ID
              instead of taking its mobile / phone number;
        :param resend_existing: check for existing notifications to update based on
          mailed recipient, otherwise create new notifications;
        :param put_in_queue: use cron to send queued SMS instead of sending them
          directly;
        """
        # sms_pid_to_number = sms_pid_to_number if sms_pid_to_number is not None else {}
        # sms_numbers = sms_numbers if sms_numbers is not None else []
        # sms_create_vals = []
        # sms_all = self.env['sms.sms'].sudo()

        # pre-compute SMS data
        body = msg_vals['body'] if msg_vals and 'body' in msg_vals else message.body
        sms_base_vals = {
            'body': html2plaintext(body),
            'mail_message_id': message.id,
            'state': 'outgoing',
        }
        #print ('===sms_base_vals==',sms_base_vals)
        notif_create_values = [{
            'author_id': message.author_id.id,
            'mail_message_id': message.id,
            'res_partner_id': 2,#sms.partner_id.id,
            # 'sms_number': sms.number,
            'notification_type': 'inbox',
            # 'sms_id': sms.id,
            'is_read': True,  # discard Inbox notification
            'notification_status': 'ready'# if sms.state == 'outgoing' else 'exception',
            # 'failure_type': '' if sms.state == 'outgoing' else sms.failure_type,
        }]# for sms in sms_all if (sms.partner_id and sms.partner_id.id not in existing_pids) or (not sms.partner_id and sms.number not in existing_numbers)]
        if notif_create_values:
            self.env['mail.notification'].sudo().create(notif_create_values)
        # notify from computed recipients_data (followers, specific recipients)
        # partners_data = [r for r in recipients_data if r['notif'] == 'sms']
        # partner_ids = [r['id'] for r in partners_data]
        # if partner_ids:
        #     for partner in self.env['res.partner'].sudo().browse(partner_ids):
        #         number = sms_pid_to_number.get(partner.id) or partner.mobile or partner.phone
        #         sanitize_res = phone_validation.phone_sanitize_numbers_w_record([number], partner)[number]
        #         number = sanitize_res['sanitized'] or number
        #         sms_create_vals.append(dict(
        #             sms_base_vals,
        #             partner_id=partner.id,
        #             number=number
        #         ))

        # # notify from additional numbers
        # if sms_numbers:
        #     sanitized = phone_validation.phone_sanitize_numbers_w_record(sms_numbers, self)
        #     tocreate_numbers = [
        #         value['sanitized'] or original
        #         for original, value in sanitized.items()
        #     ]
        #     sms_create_vals += [dict(
        #         sms_base_vals,
        #         partner_id=False,
        #         number=n,
        #         state='outgoing' if n else 'error',
        #         failure_type='' if n else 'sms_number_missing',
        #     ) for n in tocreate_numbers]

        # # create sms and notification
        # existing_pids, existing_numbers = [], []
        # if sms_create_vals:
        #     sms_all |= self.env['sms.sms'].sudo().create(sms_create_vals)

        #     if resend_existing:
        #         existing = self.env['mail.notification'].sudo().search([
        #             '|', ('res_partner_id', 'in', partner_ids),
        #             '&', ('res_partner_id', '=', False), ('sms_number', 'in', sms_numbers),
        #             ('notification_type', '=', 'sms'),
        #             ('mail_message_id', '=', message.id)
        #         ])
        #         for n in existing:
        #             if n.res_partner_id.id in partner_ids and n.mail_message_id == message:
        #                 existing_pids.append(n.res_partner_id.id)
        #             if not n.res_partner_id and n.sms_number in sms_numbers and n.mail_message_id == message:
        #                 existing_numbers.append(n.sms_number)

        #     notif_create_values = [{
        #         'author_id': message.author_id.id,
        #         'mail_message_id': message.id,
        #         'res_partner_id': sms.partner_id.id,
        #         'sms_number': sms.number,
        #         'notification_type': 'sms',
        #         'sms_id': sms.id,
        #         'is_read': True,  # discard Inbox notification
        #         'notification_status': 'ready' if sms.state == 'outgoing' else 'exception',
        #         'failure_type': '' if sms.state == 'outgoing' else sms.failure_type,
        #     } for sms in sms_all if (sms.partner_id and sms.partner_id.id not in existing_pids) or (not sms.partner_id and sms.number not in existing_numbers)]
        #     if notif_create_values:
        #         self.env['mail.notification'].sudo().create(notif_create_values)

        #     if existing_pids or existing_numbers:
        #         for sms in sms_all:
        #             notif = next((n for n in existing if
        #                          (n.res_partner_id.id in existing_pids and n.res_partner_id.id == sms.partner_id.id) or
        #                          (not n.res_partner_id and n.sms_number in existing_numbers and n.sms_number == sms.number)), False)
        #             if notif:
        #                 notif.write({
        #                     'notification_type': 'sms',
        #                     'notification_status': 'ready',
        #                     'sms_id': sms.id,
        #                     'sms_number': sms.number,
        #                 })

        # if sms_all and not put_in_queue:
        #     sms_all.filtered(lambda sms: sms.state == 'outgoing').send(auto_commit=False, raise_exception=False)

        return True

    def _message_whatsapp(self, body, subtype_id=False, partner_ids=False, number_field=False,
                     sms_numbers=None, sms_pid_to_number=None, **kwargs):
        """ Main method to post a message on a record using SMS-based notification
        method.

        :param body: content of SMS;
        :param subtype_id: mail.message.subtype used in mail.message associated
          to the sms notification process;
        :param partner_ids: if set is a record set of partners to notify;
        :param number_field: if set is a name of field to use on current record
          to compute a number to notify;
        :param sms_numbers: see ``_notify_record_by_sms``;
        :param sms_pid_to_number: see ``_notify_record_by_sms``;
        """
        self.ensure_one()
        sms_pid_to_number = sms_pid_to_number if sms_pid_to_number is not None else {}

        if number_field or (partner_ids is False and sms_numbers is None):
            info = self._sms_get_recipients_info(force_field=number_field)[self.id]
            info_partner_ids = info['partner'].ids if info['partner'] else False
            info_number = info['sanitized'] if info['sanitized'] else info['number']
            if info_partner_ids and info_number:
                sms_pid_to_number[info_partner_ids[0]] = info_number
            if info_partner_ids:
                partner_ids = info_partner_ids + (partner_ids or [])
            if info_number and not info_partner_ids:
                sms_numbers = [info_number] + (sms_numbers or [])

        if subtype_id is False:
            subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')

        return self.message_post(
            body=plaintext2html(html2plaintext(body)), partner_ids=partner_ids or [],  # TDE FIXME: temp fix otherwise crash mail_thread.py
            message_type='whatsapp', subtype_id=subtype_id,
            sms_numbers=sms_numbers, sms_pid_to_number=sms_pid_to_number,
            **kwargs
        )
    
    def _message_whatsapp_with_template(self, template=False, template_xmlid=False, template_fallback='', partner_ids=False, **kwargs):
        """ Shortcut method to perform a _message_sms with an sms.template.

        :param template: a valid sms.template record;
        :param template_xmlid: XML ID of an sms.template (if no template given);
        :param template_fallback: plaintext (jinja-enabled) in case template
          and template xml id are falsy (for example due to deleted data);
        """
        self.ensure_one()
        if not template and template_xmlid:
            template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if template:
            body = template._render_field('body', self.ids, compute_lang=True)[self.id]
        else:
            body = self.env['mail.template']._render_template(template_fallback, self._name, self.ids)[self.id]
        return self._message_whatsapp(body, partner_ids=partner_ids, **kwargs)

#     def _get_default_whatsapp_recipients(self):
#         """ This method will likely need to be overriden by inherited models.
#                :returns partners: recordset of res.partner
#         """
#         partners = self.env['res.partner']
#         if hasattr(self, 'partner_id'):
#             partners |= self.mapped('partner_id')
#         if hasattr(self, 'partner_ids'):
#             partners |= self.mapped('partner_ids')
#         return partners
# 
#     def message_post_send_whatsapp(self, whatsapp_message, numbers=None, partners=None, note_msg=None, log_error=False):
#         """ Send an SMS text message and post an internal note in the chatter if successfull
#             :param sms_message: plaintext message to send by sms
#             :param partners: the numbers to send to, if none are given it will take those
#                                 from partners or _get_default_sms_recipients
#             :param partners: the recipients partners, if none are given it will take those
#                                 from _get_default_sms_recipients, this argument
#                                 is ignored if numbers is defined
#             :param note_msg: message to log in the chatter, if none is given a default one
#                              containing the sms_message is logged
#         """
#         if not numbers:
#             if not partners:
#                 partners = self._get_default_whatsapp_recipients()
# 
#             # Collect numbers, we will consider the message to be sent if at least one number can be found
#             numbers = list(set([i.whatsapp for i in partners if i.whatsapp]))
#         if numbers:
#             try:
#                 self.env.user.company_id._send_whatsapp(numbers, whatsapp_message)
#                 mail_message = note_msg or _('Whatsapp message sent: %s') % whatsapp_message
# 
#             except InsufficientCreditError as e:
#                 if not log_error:
#                     raise e
#                 mail_message = _('Insufficient credit, unable to send Whatsapp message: %s') % whatsapp_message
#         else:
#             mail_message = _('No whatsapp number defined, unable to send SMS message: %s') % whatsapp_message
# 
#         for thread in self:
#             thread.message_post(body=mail_message)
#         return False
