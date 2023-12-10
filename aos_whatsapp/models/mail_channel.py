from odoo import api, fields, models, _, Command
import requests
import json
import logging
import re
import ast
import base64
from markupsafe import Markup

from datetime import timedelta
from odoo import tools
from odoo.tools.mimetypes import guess_mimetype
from odoo.exceptions import UserError, ValidationError

from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    # @api.returns('mail.message', lambda value: value.id)
    # def message_post(self, *, message_type='whatsapp', **kwargs):
    #     if not self.env.user:
    #         #GET PUBLIC USER WHEN EMPTY
    #         self.env.user = self.env['res.users'].sudo().search([('active','=',False),('login','=','public')], limit=1)
    #     print ('==MailThread==',self.env.user)
    #     return super(MailThread, self).message_post(**kwargs)

# class MailMessage(models.Model):
#     _inherit = 'mail.message'

#     whatsapp_numbers = fields.Char()

# class ChannelPartner(models.Model):
#     _inherit = 'mail.channel.partner'

#     @api.model_create_multi
#     def create(self, vals_list):
#         """Similar access rule as the access rule of the mail channel.

#         It can not be implemented in XML, because when the record will be created, the
#         partner will be added in the channel and the security rule will always authorize
#         the creation.
#         """
#         #print ('===CHANNEL PARTNER==',vals_list)
#         if len(vals_list) == 2:
#             if not vals_list[1]['partner_id']:
#                 partner_id = self.env['res.users'].sudo().search([('active','=',False),('login','=','public')], limit=1)
#                 vals_list[1].update({'partner_id': partner_id.id})
#         return super(ChannelPartner, self).create(vals_list)

class mailChannel(models.Model):
    _inherit = 'mail.channel'

    channel_type = fields.Selection(
        selection_add=[('whatsapp', 'WhatsApp Conversation')],
        ondelete={'whatsapp': 'cascade'})
    whatsapp_number = fields.Char(string="Phone Number")
    whatsapp_channel_valid_until = fields.Datetime(string="WhatsApp Partner Last Message Datetime", compute="_compute_whatsapp_channel_valid_until")
    whatsapp_partner_id = fields.Many2one(comodel_name='res.partner', string="WhatsApp Partner")
    whatsapp_mail_message_id = fields.Many2one(comodel_name='mail.message', string="Related message", index="btree_not_null")
    wa_account_id = fields.Many2one(comodel_name='ir.whatsapp_server', string="WhatsApp Klikodoo")
    senderkeyhash = fields.Char()
    recipientkeyhash = fields.Char()
    #path_id = fields.Many2one('api.rest.path', string="Whatsapp Path")
    
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *, message_type='whatsapp', **kwargs):
        message = super(mailChannel, self).message_post(message_type=message_type, **kwargs)
        print ('===KIRIM BALIK==',self._context)
        if not self._context.get('from_odoobot') and self._context.get('uid'):
            self.send_whatsapp_message(self.message_ids, kwargs, message)
        return message

    # def _generate_attachment_from_report(self, record=False):
    #     """Create attachment from report if relevant"""
    #     if record and self.header_type == 'document' and self.report_id:
    #         report_content, report_format = self.report_id._render_qweb_pdf(self.report_id, record.id)
    #         if self.report_id.print_report_name:
    #             report_name = safe_eval(self.report_id.print_report_name, {'object': record}) + '.' + report_format
    #         else:
    #             report_name = self.display_name + '.' + report_format
    #         return self.env['ir.attachment'].create({
    #             'name': report_name,
    #             'raw': report_content,
    #             'mimetype': 'application/pdf',
    #         })
    #     return self.env['ir.attachment']

    @api.depends('message_ids')
    def _compute_whatsapp_channel_valid_until(self):
        self.whatsapp_channel_valid_until = False
        wa_channels = self.filtered(lambda c: c.channel_type == 'whatsapp')
        if wa_channels:
            channel_last_msg_ids = {
                r['id']: r['message_id']
                for r in wa_channels._channel_last_whatsapp_partner_id_message_ids()
            }
            MailMessage = self.env['mail.message'].with_prefetch(list(channel_last_msg_ids.values()))
            for channel in wa_channels:
                last_msg_id = channel_last_msg_ids.get(channel.id, False)
                if not last_msg_id:
                    continue
                channel.whatsapp_channel_valid_until = MailMessage.browse(last_msg_id).create_date + timedelta(hours=24)

    
    def _channel_last_whatsapp_partner_id_message_ids(self):
        """ Return the last message of the whatsapp_partner_id given whatsapp channels."""
        if not self:
            return []
        self.env['mail.message'].flush_model()
        self.env.cr.execute("""
              SELECT res_id AS id, MAX(mm.id) AS message_id
                FROM mail_message AS mm
                JOIN mail_channel AS dc ON mm.res_id = dc.id
               WHERE mm.model = 'mail.channel'
                 AND mm.res_id IN %s
                 AND mm.author_id = dc.whatsapp_partner_id
            GROUP BY mm.res_id
            """, [tuple(self.ids)])
        return self.env.cr.dictfetchall()

    # def message_post(self, *, message_type='notification', **kwargs):
    #     new_msg = super().message_post(message_type=message_type, **kwargs)
    #     print ('===KIRIM BALIK==',self._context,self.channel_type,message_type)
    #     if self.channel_type == 'whatsapp' and message_type == 'whatsapp':
    #         if new_msg.author_id == self.whatsapp_partner_id:
    #             self.env['bus.bus']._sendone(self, 'mail.channel/whatsapp_channel_valid_until_changed', {
    #                 'id': self.id,
    #                 'whatsapp_channel_valid_until': self.whatsapp_channel_valid_until,
    #             })
    #         if not new_msg.wa_message_ids:
    #             whatsapp_message = self.env['mail.message'].create({
    #                 'body': new_msg.body,
    #                 'whatsapp_message_id': new_msg.id,
    #                 'message_type': 'whatsapp',
    #                 'whatsapp_numbers': f'+{self.whatsapp_number}',
    #                 'whatsapp_server_id': self.wa_account_id.id,
    #             })
    #             whatsapp_message._send()
    #     return new_msg

    # ------------------------------------------------------------
    # CONTROLLERS
    # ------------------------------------------------------------

    @api.returns('self')
    def _get_whatsapp_channel(self, whatsapp_number, wa_account_id, sender_name=False, create_if_not_found=False, related_message=False):
        """ Creates a whatsapp channel.
            :param str whatsapp_number: whatsapp phone number. The whatsapp phone number of the partner
            :returns: channel
        """
        related_record = False
        responsible_partners = self.env['res.partner']
        IrModel = self.env['ir.model']
        channel_domain = [
            ('whatsapp_number', '=', whatsapp_number),
            ('wa_account_id', '=', wa_account_id.id)
        ]
        # if related_message:
        #     related_record = self.env[related_message.model].browse(related_message.res_id)
        #     responsible_partners = related_record._whatsapp_get_responsible(
        #         related_message=related_message,
        #         related_record=related_record,
        #         whatsapp_account=wa_account_id,
        #     ).partner_id

        #     if 'message_ids' in related_record:
        #         record_messages = related_record.message_ids
        #     else:
        #         record_messages = self.env['mail.message'].search([
        #             ('model', '=', related_record._name),
        #             ('res_id', '=', related_record.id),
        #             ('message_type', '!=', 'user_notification'),
        #         ])
        #     channel_domain += [
        #         ('whatsapp_mail_message_id', 'in', record_messages.ids),
        #     ]
        channel = self.sudo().search(channel_domain, order='create_date desc', limit=1)
        print ('==_get_whatsapp_channel=channel_domain==',channel,channel_domain)

        if responsible_partners:
            channel = channel.filtered(lambda c: all(r in c.channel_member_ids.partner_id for r in responsible_partners))

        partners_to_notify = responsible_partners
        record_name = related_message.record_name
        if not record_name and related_message.res_id:
            record_name = self.env[related_message.model].browse(related_message.res_id).name
        if not channel and create_if_not_found:
            channel = self.sudo().with_context(tools.clean_context(self.env.context)).create({
                'name': f"{whatsapp_number} ({record_name})" if record_name else whatsapp_number,
                'channel_type': 'whatsapp',
                'whatsapp_number': whatsapp_number,
                'whatsapp_partner_id': self.env['res.partner']._find_or_create_from_number(whatsapp_number, sender_name).id,
                'wa_account_id': wa_account_id.id,
                'whatsapp_mail_message_id': related_message.id if related_message else None,
            })
            partners_to_notify += channel.whatsapp_partner_id
            if related_message:
                # Add message in channel about the related document
                info = _("Related %(model_name)s:", model_name=IrModel._get(related_message.model).display_name)
                url = Markup('{base_url}/web#model={model}&id={res_id}').format(
                    base_url=self.get_base_url(), model=related_message.model, res_id=related_message.res_id)
                related_record_name = related_message.record_name
                if not related_record_name:
                    related_record_name = self.env[related_message.model].browse(related_message.res_id).display_name
                channel.message_post(
                    body=Markup('<p>{info}<a target="_blank" href="{url}">{related_record_name}</a></p>').format(
                        info=info, url=url, related_record_name=related_record_name),
                    message_type='comment',
                    author_id=self.env.ref('base.partner_root').id,
                    subtype_xmlid='mail.mt_note',
                )
                if hasattr(related_record, 'message_post'):
                    # Add notification in document about the new message and related channel
                    info = _("A new WhatsApp channel is created for this document")
                    url = Markup('{base_url}/web#model=discuss.channel&id={channel_id}').format(
                        base_url=self.get_base_url(), channel_id=channel.id)
                    related_record.message_post(
                        author_id=self.env.ref('base.partner_root').id,
                        body=Markup('<p>{info}<a target="_blank" class="o_whatsapp_channel_redirect"'
                                    'data-oe-id="{channel_id}" href="{url}">{channel_name}</a></p>').format(
                                        info=info, url=url, channel_id=channel.id, channel_name=channel.display_name),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note',
                    )
            if partners_to_notify == channel.whatsapp_partner_id and wa_account_id.notify_user_ids.partner_id:
                partners_to_notify += wa_account_id.notify_user_ids.partner_id
            channel.channel_member_ids = [Command.clear()] + [Command.create({'partner_id': partner.id}) for partner in partners_to_notify]
            channel._broadcast(partners_to_notify.ids)
        return channel

    def convert_email_from_to_name(self, str1):
        result = re.search('"(.*)"', str1)
        return result.group(1)

    def custom_html2plaintext(self, html):
        html = re.sub('<br\s*/?>', '\n', html)
        html = re.sub('<.*?>', ' ', html)
        return html

    def send_whatsapp_message(self, message_ids, kwargs, message_id):
        partner_id = False
        WhatsappServer = self.env['ir.whatsapp_server']
        whatsapp_id = WhatsappServer.search([('status','=','authenticated')], order='sequence asc', limit=1)
        whatsapp_endpoint = 'https://klikodoo.id/api/wa'
        whatsapp_instance = whatsapp_id.klik_key
        whatsapp_token = whatsapp_id.klik_secret
        # if 'author_id' in kwargs and kwargs.get('author_id'):
        #     partner_id = self.channel_last_seen_partner_ids
        #     partner_id = self.env['res.partner'].search([('id', '=', kwargs.get('author_id'))])
        partner_ids = message_ids.mapped('author_id')
        attachment_ids = message_ids.mapped('attachment_ids')
        whatsapp_numbers = list(filter(None, [*set(message_ids.mapped('whatsapp_numbers'))]))
        print ('==whatsapp_numbers==',whatsapp_numbers,partner_ids,kwargs)
        print ('===attachment_ids==',attachment_ids)
        if whatsapp_numbers:#partner_ids and message_id.author_id and not partner_id:
            #print ('-channel_last_seen_partner_ids--',self.channel_last_seen_partner_ids,self.channel_partner_ids)
            #print ('--send_whatsapp_message-from livechat to whatsapp-client',partner_ids, list(filter(None, [*set(whatsapp_numbers)])), kwargs, message_id)
            #partner.user_ids and all(user.has_group('base.group_user') for user in partner.user_ids)
            #partners = partner_ids.filtered(lambda p: p != message_id.author_id)
            #print ('===partner_id===',partner_id)
            #Param = self.env['res.config.settings'].sudo().get_values()
            #no_phone_partners = []
            invalid_whatsapp_number_partner = []
            if whatsapp_endpoint and whatsapp_token:
                status_url = whatsapp_endpoint + '/auth/' + whatsapp_instance + '/' + whatsapp_token + '/status'
                #print ('=status_url==',status_url,partner_id)
                status_response = requests.get(status_url, data=json.dumps({}), headers={'Content-Type': 'application/json'})
                json_response_status = json.loads(status_response.text)['result']
                # status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
                # status_response = requests.get(status_url)
                # json_response_status = json.loads(status_response.text)
                #print ('-send_whatsapp_message-',status_response,json_response_status,partner_id,partner_ids,partner_id.name,partner_id.country_id.phone_code, partner_id.mobile,partner_id.whatsapp)
                for whatsapp_number in whatsapp_numbers:
                    if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status['accountStatus'] == 'authenticated':
                    #if partner_id.country_id.phone_code and partner_id.whatsapp:
                        #whatsapp_msg_number = partner_id.whatsapp
                        # whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "");
                        # whatsapp_msg_number_without_strip = whatsapp_msg_number_without_space.replace("-", "")
                        # whatsapp_msg_number_without_code = whatsapp_msg_number_without_strip.replace(
                        #     '+' + str(partner_id.country_id.phone_code), "")
                        # phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get('whatsapp_token') + '&phone=' + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                        # phone_exists_response = requests.get(phone_exists_url)
                        # json_response_phone_exists = json.loads(phone_exists_response.text)
                        # phone_exists_url = whatsapp_endpoint + '/check/' + whatsapp_instance + '/' + whatsapp_token
                        # phone_exists_response = requests.get(phone_exists_url, data=json.dumps({'phone': str(partner_id.country_id.phone_code) + whatsapp_msg_number_without_code}), headers={'Content-Type': 'application/json'})
                        # json_response_phone_exists = json.loads(phone_exists_response.text)['result']
                        # print ('==phone_exists_response==',phone_exists_url,str(partner_id.country_id.phone_code) + whatsapp_msg_number_without_code,phone_exists_response,phone_exists_response.status_code,json_response_phone_exists)
                        # if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and json_response_phone_exists['result'] == 'exists':
                        #_logger.info("\nPartner phone exists")
                        # url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                        # headers = {
                        #     "Content-Type": "application/json",
                        # }
                        url = whatsapp_endpoint + '/post'
                        headers = {"Content-Type": "application/json"}
                        html_to_plain_text = self.custom_html2plaintext(kwargs.get('body'))

                        # if kwargs.get('email_from'):
                        #     if '<' in kwargs.get('email_from') and '>' in kwargs.get('email_from'):
                        #         tmp_dict = {
                        #             'params' : {
                        #                 "phone": whatsapp_number,
                        #                 "body": self.convert_email_from_to_name(kwargs.get('email_from'))+''+ str(self.id) + ': '+ html_to_plain_text,
                        #                 'instance': whatsapp_instance,
                        #                 'key': whatsapp_token,
                        #                 'method': 'sendMessage',
                        #             }
                        #         }
                        #     else:
                        #         tmp_dict = {
                        #             'params' : {
                        #                 "phone": whatsapp_number,
                        #                 "body": kwargs.get('email_from')+ '' + str(self.id) + ': ' + html_to_plain_text,
                        #                 'instance': whatsapp_instance,
                        #                 'key': whatsapp_token,
                        #                 'method': 'sendMessage',
                        #             }
                        #         }
                        # else:
                        #     tmp_dict = {
                        #         'params' : {
                        #             "phone": whatsapp_number,
                        #             "body": html_to_plain_text,
                        #             'instance': whatsapp_instance,
                        #             'key': whatsapp_token,
                        #             'method': 'sendMessage',
                        #         }
                        #     }
                        # message_dict = {
                        #     'params' : {
                        #         "phone": whatsapp_number,
                        #         "body": html_to_plain_text,
                        #         'instance': whatsapp_instance,
                        #         'key': whatsapp_token,
                        #         'method': 'sendMessage',
                        #     }
                        # }
                        if kwargs.get('attachment_ids'):
                            # message_attach = {
                            #     'method': 'sendFile',
                            #     'phone': whatsapp,
                            #     'chatId': partner.chat_id or '',
                            #     'body': att['datas'].split(",")[0],
                            #     'filename': att['filename'],
                            #     'caption': message.replace('_PARTNER_', partner.name).replace('_NUMBER_', origin).replace('_AMOUNT_TOTAL_', str(self.format_amount(amount_total, currency_id)) if currency_id else '').replace('\xa0', ' '),#att['caption'],
                            #     'origin': origin,
                            #     'link': link,
                            # }
                            for attachment in self.env['ir.attachment'].browse(kwargs.get('attachment_ids')):
                                mimetype = guess_mimetype(base64.b64decode(attachment.datas))
                                if mimetype == 'application/octet-stream':
                                    mimetype = 'video/mp4'
                                str_mimetype = 'data:' + mimetype + ';base64,'
                                datas = str_mimetype + str(attachment.datas.decode("utf-8"))
                                attachment_dict = {
                                    'params' : {
                                        'method': 'sendFile',
                                        'filename': attachment.name,
                                        "phone": whatsapp_number,
                                        "body": datas,
                                        'instance': whatsapp_instance,
                                        'key': whatsapp_token,
                                    }
                                }
                                #print ('=attachment==',attachment.datas.split(",")[0])
                                #attachment_dict['params'].update({'method': 'sendFile', 'body': datas, 'filename': attachment.name})
                                response = requests.post(url, json.dumps(attachment_dict), headers=headers)
                        else:
                            message_dict = {
                                'params' : {
                                    'method': 'sendMessage',
                                    "phone": whatsapp_number,
                                    "body": html_to_plain_text,
                                    'instance': whatsapp_instance,
                                    'key': whatsapp_token,
                                }
                            }
                            #print ('----tmp_dict---',kwargs,tmp_dict)
                            response = requests.post(url, json.dumps(message_dict), headers=headers)
                        if response.status_code == 201 or response.status_code == 200:
                            _logger.info("\nSend Message successfully")
                            response_dict = response.json()
                                #message_id.with_context({'from_odoobot': True}).write({'whatsapp_message_id': response_dict.get('id')})
                            # else:
                            #     invalid_whatsapp_number_partner.append(partner_id.name)
                        # else:
                        #     no_phone_partners.append(partner_id.name)
                    else:
                        raise UserError(_('Please authorize your mobile number with klikodoo'))
            if len(invalid_whatsapp_number_partner) >= 1:
                raise UserError(_('Please add valid whatsapp number for %s customer')% ', '.join(invalid_whatsapp_number_partner))

    # def send_whatsapp_message(self, partner_ids, kwargs, message_id):
    #     print ('--send_whatsapp_message--',partner_ids, kwargs, message_id)
    #     partner_id = False
    #     WhatsappServer = self.env['ir.whatsapp_server']
    #     whatsapp_id = WhatsappServer.search([('status','=','authenticated')], order='sequence asc', limit=1)
    #     whatsapp_endpoint = 'https://klikodoo.id/api/wa'
    #     whatsapp_instance = whatsapp_id.klik_key
    #     whatsapp_token = whatsapp_id.klik_secret
    #     if 'author_id' in kwargs and kwargs.get('author_id'):
    #         partner_id = self.env['res.partner'].search([('id', '=', kwargs.get('author_id'))])
    #     if message_id.author_id and not partner_id:
    #         partner_id = message_id.author_id
    #         #print ('===partner_id===',partner_id)
    #         #Param = self.env['res.config.settings'].sudo().get_values()
    #         no_phone_partners = []
    #         invalid_whatsapp_number_partner = []
    #         if whatsapp_endpoint and whatsapp_id.klik_secret:
    #             status_url = whatsapp_endpoint + '/auth/' + whatsapp_instance + '/' + whatsapp_token + '/status'
    #             print ('=status_url==',status_url)
    #             status_response = requests.get(status_url, data=json.dumps({}), headers={'Content-Type': 'application/json'})
    #             json_response_status = json.loads(status_response.text)['result']
    #             # status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
    #             # status_response = requests.get(status_url)
    #             # json_response_status = json.loads(status_response.text)
    #             print ('-send_whatsapp_message-',json_response_status,partner_id,partner_id.name,partner_id.country_id.phone_code, partner_id.mobile)
    #             if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status['accountStatus'] == 'authenticated':
    #                 if partner_id.country_id.phone_code and partner_id.mobile:
    #                     whatsapp_msg_number = partner_id.mobile
    #                     whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "");
    #                     whatsapp_msg_number_without_strip = whatsapp_msg_number_without_space.replace("-", "")
    #                     whatsapp_msg_number_without_code = whatsapp_msg_number_without_strip.replace(
    #                         '+' + str(partner_id.country_id.phone_code), "")
    #                     # phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get('whatsapp_token') + '&phone=' + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
    #                     # phone_exists_response = requests.get(phone_exists_url)
    #                     # json_response_phone_exists = json.loads(phone_exists_response.text)
    #                     # phone_exists_url = whatsapp_endpoint + '/check/' + whatsapp_instance + '/' + whatsapp_token
    #                     # phone_exists_response = requests.get(phone_exists_url, data=json.dumps({'phone': str(partner_id.country_id.phone_code) + whatsapp_msg_number_without_code}), headers={'Content-Type': 'application/json'})
    #                     # json_response_phone_exists = json.loads(phone_exists_response.text)['result']
    #                     # print ('==phone_exists_response==',phone_exists_url,str(partner_id.country_id.phone_code) + whatsapp_msg_number_without_code,phone_exists_response,phone_exists_response.status_code,json_response_phone_exists)
    #                     # if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and json_response_phone_exists['result'] == 'exists':
    #                     _logger.info("\nPartner phone exists")
    #                     # url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
    #                     # headers = {
    #                     #     "Content-Type": "application/json",
    #                     # }
    #                     url = whatsapp_endpoint + '/post'
    #                     headers = {"Content-Type": "application/json"}
    #                     html_to_plain_text = self.custom_html2plaintext(kwargs.get('body'))

    #                     if kwargs.get('email_from'):
    #                         if '<' in kwargs.get('email_from') and '>' in kwargs.get('email_from'):
    #                             tmp_dict = {
    #                                 'params' : {
    #                                     "phone": str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
    #                                     "body": self.convert_email_from_to_name(kwargs.get('email_from'))+''+ str(self.id) + ': '+ html_to_plain_text,
    #                                     'instance': whatsapp_instance,
    #                                     'key': whatsapp_token,
    #                                     'method': 'sendMessage',
    #                                 }
    #                             }
    #                         else:
    #                             tmp_dict = {
    #                                 'params' : {
    #                                     "phone": str(
    #                                         partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
    #                                     "body": kwargs.get('email_from')+ '' + str(self.id) + ': ' + html_to_plain_text,
    #                                     'instance': whatsapp_instance,
    #                                     'key': whatsapp_token,
    #                                     'method': 'sendMessage',
    #                                 }
    #                             }
    #                     else:
    #                         tmp_dict = {
    #                             'params' : {
    #                                 "phone": str(
    #                                     partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
    #                                 "body": html_to_plain_text,
    #                                 'instance': whatsapp_instance,
    #                                 'key': whatsapp_token,
    #                                 'method': 'sendMessage',
    #                             }
    #                         }
    #                     print ('----tmp_dict---',tmp_dict)
    #                     response = requests.post(url, json.dumps(tmp_dict), headers=headers)
    #                     if response.status_code == 201 or response.status_code == 200:
    #                         _logger.info("\nSend Message successfully")
    #                         response_dict = response.json()
    #                         #message_id.with_context({'from_odoobot': True}).write({'whatsapp_message_id': response_dict.get('id')})
    #                     # else:
    #                     #     invalid_whatsapp_number_partner.append(partner_id.name)
    #                 else:
    #                     no_phone_partners.append(partner_id.name)
    #             else:
    #                 raise UserError(_('aPlease authorize your mobile number with chat api'))
    #         if len(invalid_whatsapp_number_partner) >= 1:
    #             raise UserError(_('Please add valid whatsapp number for %s customer')% ', '.join(invalid_whatsapp_number_partner))
    #     else:
    #         no_phone_partners = []
    #         invalid_whatsapp_number_partner = []
    #         for partner_id in partner_ids:
    #             if whatsapp_endpoint and whatsapp_token:
    #                 status_url = whatsapp_endpoint + '/auth/' + whatsapp_instance + '/' + whatsapp_token + '/status'
    #                 status_response = requests.get(status_url, data=json.dumps({}), headers={'Content-Type': 'application/json'})
    #                 json_response_status = json.loads(status_response.text)['result']
    #                 # status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
    #                 # status_response = requests.get(status_url)
    #                 # json_response_status = json.loads(status_response.text)
    #                 if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status[
    #                     'accountStatus'] == 'authenticated':
    #                     if partner_id.country_id.phone_code and partner_id.mobile:
    #                         whatsapp_msg_number = partner_id.mobile
    #                         whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "");
    #                         whatsapp_msg_number_without_strip = whatsapp_msg_number_without_space.replace("-", "")
    #                         whatsapp_msg_number_without_code = whatsapp_msg_number_without_strip.replace(
    #                             '+' + str(partner_id.country_id.phone_code), "")
    #                         # phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get(
    #                         #     'whatsapp_token') + '&phone=' + str(
    #                         #     partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
    #                         # phone_exists_response = requests.get(phone_exists_url)
    #                         # json_response_phone_exists = json.loads(phone_exists_response.text)
    #                         # phone_exists_url = whatsapp_endpoint + '/check/' + whatsapp_instance + '/' + whatsapp_token
    #                         # phone_exists_response = requests.get(url, data=json.dumps({'phone': str(res_partner_id.country_id.phone_code) + whatsapp_msg_number_without_code}), headers={'Content-Type': 'application/json'})
    #                         # json_response_phone_exists = json.loads(phone_exists_response.text)['result']
    #                         # if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and \
    #                         #         json_response_phone_exists['result'] == 'exists':
    #                         _logger.info("\nPartner phone exists")
    #                         # url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
    #                         # headers = {
    #                         #     "Content-Type": "application/json",
    #                         # }
    #                         url = whatsapp_endpoint + '/post'
    #                         headers = {"Content-Type": "application/json"}
    #                         html_to_plain_text = self.custom_html2plaintext(kwargs.get('body'))
    #                         if kwargs.get('email_from'):
    #                             if '<' in kwargs.get('email_from') and '>' in kwargs.get('email_from'):
    #                                 tmp_dict = {
    #                                     'params' : {
    #                                         "phone": str(
    #                                             partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
    #                                         "body": self.convert_email_from_to_name(kwargs.get('email_from')) + '' + str(
    #                                             self.id) + ': ' + html_to_plain_text,   
    #                                         'instance': whatsapp_instance,
    #                                         'key': whatsapp_token,
    #                                         'method': 'sendMessage',
    #                                     }
    #                                 }
    #                             else:
    #                                 tmp_dict = {
    #                                     'params' : {
    #                                         "phone": str(
    #                                             partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
    #                                         "body": kwargs.get('email_from') + '' + str(self.id) + ': ' + html_to_plain_text,   
    #                                         'instance': whatsapp_instance,
    #                                         'key': whatsapp_token,
    #                                         'method': 'sendMessage',
    #                                     }
    #                                 }
    #                         else:
    #                             tmp_dict = {
    #                                 'params' : {
    #                                     "phone": str(
    #                                         partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
    #                                     "body": html_to_plain_text,   
    #                                     'instance': whatsapp_instance,
    #                                     'key': whatsapp_token,
    #                                     'method': 'sendMessage',
    #                                     }
    #                             }
    #                         response = requests.post(url, json.dumps(tmp_dict), headers=headers)
    #                         if response.status_code == 201 or response.status_code == 200:
    #                             _logger.info("\nSend Message successfully")
    #                             response_dict = response.json()
    #                             #message_id.with_context({'from_odoobot': True}).write({'whatsapp_message_id': response_dict.get('id')})
    #                         # else:
    #                         #     invalid_whatsapp_number_partner.append(partner_id.name)
    #                     else:
    #                         no_phone_partners.append(partner_id.name)
    #                 else:
    #                     raise UserError(_('bPlease authorize your mobile number with chat api'))

    #     if len(invalid_whatsapp_number_partner) >= 1:
    #         raise UserError(
    #             _('Please add valid whatsapp number for %s customer') % ', '.join(invalid_whatsapp_number_partner))
