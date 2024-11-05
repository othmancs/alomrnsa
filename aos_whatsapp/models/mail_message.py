# See LICENSE file for full copyright and licensing details.

import ast
import base64
from odoo import fields, models, _, sql_db, api, tools
from odoo.tools.mimetypes import guess_mimetype
from odoo.exceptions import Warning, UserError
from datetime import datetime
import html2text
from ..klikapi import texttohtml

import threading
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class MailMessage(models.Model):
    _inherit = 'mail.message'

    _ACTIVE_THRESHOLD_DAYS = 15

    message_type = fields.Selection(selection_add=[('whatsapp', 'Whatsapp')], ondelete={'whatsapp': 'set default'})   
    whatsapp_message_type = fields.Selection([
        ('outbound', 'Outbound'),
        ('inbound', 'Inbound')], string="Message Type", default='outbound') 
    whatsapp_server_id = fields.Many2one('ir.whatsapp_server', string='Whatsapp Server')
    whatsapp_method = fields.Char('Method', default='sendMessage')
    whatsapp_status = fields.Selection([('pending','Pending'),('send', 'Sent'),('error', 'Error')], default='pending', string='Whatsapp Status')
    whatsapp_response = fields.Text('Response', readonly=True)
    whatsapp_data = fields.Text('Data', readonly=False)
    whatsapp_chat_id = fields.Char(string='ChatId')
    whatsapp_numbers = fields.Char()
    whatsapp_message_id = fields.Many2one('mail.message', string="Parent")
    wa_message_ids = fields.One2many('mail.message', 'whatsapp_message_id', string='Related WhatsApp Messages')

    # @api.model
    # def create(self, vals):
    #     # if vals.get('whatsapp_data'):
    #     #     vals['whatsapp_data'] = str(vals['whatsapp_data']).replace("'",'*').replace('"',"*")
    #     print ('===vals===',vals)
    #     return super(MailMessage, self).create(vals)
    
    # def _send(self, force_send_by_cron=False):
    #     if len(self) <= 1 and not force_send_by_cron:
    #         self._send_message()
    #     else:
    #         self.env.ref('aos_whatsapp.ir_cron_whatsapp_mail_message_erro_cron')._trigger()

    @api.model
    def _resend_whatsapp_message_resend(self, KlikApi):
        # print ('===s===',KlikApi)
        try:
            #new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            #uid, context = self.env.uid, self.env.context
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            with tools.mute_logger('odoo.sql_db'):
                #self.env = api.Environment(new_cr, uid, context)
                MailMessage = self.env['mail.message'].search([('message_type','=','whatsapp'),('whatsapp_status', '=', 'pending')], limit=50)
                #print ('==sMailMessage==',MailMessage)
                #if not MailMessage.whatsapp_data
                get_version = self.env["ir.module.module"].sudo().search([('name','=','base')], limit=1).latest_version
                for mail in MailMessage.filtered(lambda m: m.whatsapp_data):
                    try:
                        if not mail.whatsapp_data:
                            mail.whatsapp_status = 'error'
                            mail.whatsapp_response = 'No Message Datas'
                        # data = json.loads(str(mail.whatsapp_data.replace("'",'"')))
                        data = str(mail.whatsapp_data).replace("'",'"')
                        try:
                            # Load the JSON string
                            fixed_json_string = json.loads(data)
                            # Dump the data back to a properly formatted JSON string
                            data = json.dumps(fixed_json_string, indent=4)
                            #print(data)
                        except json.JSONDecodeError as e:
                            _logger.warning("Invalid JSON: {e}")
                        data = json.loads(data)
                        message_data = {
                            'chatId': mail.whatsapp_chat_id,
                            'body': texttohtml.formatText(mail.body),#html2text.html2text(mail.body),
                            'phone': data.get('phone') or '',
                            'origin': data.get('origin') or '',
                            'link': data.get('link') or '',
                            'get_version': get_version,
                        }
                        # print ('==body==',mail.body)
                        # print ('==html2text==',html2text.html2text(mail.body))
                        if mail.whatsapp_method == 'sendFile' and mail.attachment_ids:
                            #KLO ADA ATTACHMENT LEBIH DARI SATU
                            send_message_response = []
                            whatsapp_status = 'error'
                            i = 1
                            # attach = [att for att in mail.attachment_ids][0]#.datas
                            for attach in mail.attachment_ids:
                                mimetype = guess_mimetype(base64.b64decode(attach.datas))
                                if mimetype == 'application/octet-stream':
                                    mimetype = 'video/mp4'
                                str_mimetype = 'data:' + mimetype + ';base64,'
                                attachment = str_mimetype + str(attach.datas.decode("utf-8"))
                                message_data.update({'body': attachment, 'filename': attach.name, 'caption': data.get('caption') if i == 1 else ''})
                                data_message = json.dumps(message_data)
                                send_message = KlikApi.post_request(method=mail.whatsapp_method, data=data_message)
                                if send_message.get('message')['sent']:
                                    whatsapp_status = 'send'
                                    send_message_response.append(attach.name + ': ' + str(send_message))
                                    # mail.whatsapp_response += send_message
                                    _logger.warning('%s. Success send Attachment %s to WhatsApp %s', str(i), attach.name, data.get('phone'))
                                else:
                                    whatsapp_status = 'error'
                                    send_message_response.append(attach.name + ': ' + str(send_message))
                                    # mail.whatsapp_response += send_message
                                    _logger.warning('%s. Failed send Attachment %s to WhatsApp %s', str(i), attach.name, data.get('phone'))
                                i += 1
                            # print ('==send_message_res?ponse==',send_message_response)
                            mail.whatsapp_status = whatsapp_status
                            mail.whatsapp_response = '\n'.join(send_message_response)
                            new_cr.commit()
                        else:
                            #KLO GA ADA ATTACHMENT
                            data_message = json.dumps(message_data)
                            send_message = KlikApi.post_request(method=mail.whatsapp_method, data=data_message)
                            if send_message.get('message')['sent']:
                                mail.whatsapp_status = 'send'
                                mail.whatsapp_response = send_message
                                _logger.warning('Success send Message to WhatsApp %s', data.get('phone'))
                            else:
                                mail.whatsapp_status = 'error'
                                mail.whatsapp_response = send_message
                                _logger.warning('Failed send Message to WhatsApp %s', data.get('phone'))
                            new_cr.commit()
                        # if mail.whatsapp_method == 'sendFile' and mail.attachment_ids:
                        #     attach = [att for att in mail.attachment_ids][0]#.datas
                        #     mimetype = guess_mimetype(base64.b64decode(attach.datas))
                        #     if mimetype == 'application/octet-stream':
                        #         mimetype = 'video/mp4'
                        #     str_mimetype = 'data:' + mimetype + ';base64,'
                        #     attachment = str_mimetype + str(attach.datas.decode("utf-8"))
                        #     message_data.update({'body': attachment, 'filename': [att for att in mail.attachment_ids][0].name, 'caption': data.get('caption')})
                        # #print ('==data_message==',message_data)
                        # data_message = json.dumps(message_data)
                        # # print ('==data_message==',mail.whatsapp_method)
                        # try:
                        #     send_message = KlikApi.post_request(method=mail.whatsapp_method, data=data_message)
                        #     if send_message.get('message')['sent']:
                        #         mail.whatsapp_status = 'send'
                        #         mail.whatsapp_response = send_message
                        #         _logger.warning('Success send Message to WhatsApp number %s', data.get('phone'))
                        #     else:
                        #         mail.whatsapp_status = 'error'
                        #         mail.whatsapp_response = send_message
                        #         _logger.warning('Failed send Message to WhatsApp number %s', data.get('phone'))
                        # except:
                        #     mail.whatsapp_status = 'error'
                        #     mail.whatsapp_response = 'Response Error on Server'
                        #     _logger.warning('Failed send Message to WhatsApp number %s', data.get('phone'))
                        # new_cr.commit()
                    finally:
                        pass
        finally:
            pass

    @api.model
    def resend_whatsapp_mail_message(self):
        """Resend whatsapp error message via threding.""" 
        WhatsappServer = self.env['ir.whatsapp_server']
        whatsapp_ids = WhatsappServer.search([('status','=','authenticated')], order='sequence asc')
        #if len(whatsapp_ids) == 1:            
        # print ('==resend_whatsapp_mail_message==',whatsapp_ids,whatsapp_ids.mapped('message_response'))#.filtered(lambda ws: not ast.literal_eval(str(ws.message_response))))
        try:
            #print ('==resend_whatsapp_mail_message==',whatsapp_ids,whatsapp_ids.mapped('message_response'))
            for wserver in whatsapp_ids.filtered(lambda ws: not ast.literal_eval(str(ws.message_response))['block']):
                #company_id = self.env.user.company_id
                if wserver.status != 'authenticated':
                    _logger.warning('Whatsapp Authentication Failed!\nConfigure Whatsapp Configuration in General Setting.')
                KlikApi = wserver.klikapi()
                KlikApi.auth()
                thread_start = threading.Thread(target=self._resend_whatsapp_message_resend(KlikApi))
                thread_start.start()
        except Exception:
            _logger.exception('Error while checking whatapp connection')
        return True