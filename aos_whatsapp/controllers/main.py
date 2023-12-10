# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hashlib
import hmac
import json
import logging
from markupsafe import Markup
from werkzeug.exceptions import Forbidden

from http import HTTPStatus
from odoo import http, _
from odoo.http import request
from odoo.tools import consteq

_logger = logging.getLogger(__name__)


class Webhook(http.Controller):

    @http.route('/webhook/test', type="json", auth='public', methods=['POST'])
    def some_html(self, **kw):
        return {
            'success': True,
            'status': 'OK',
            'code': 200
        }
    
    @http.route('/webhook/partner', type="json", auth='public', methods=['GET'])
    def webhook_partner(self, **kw):
        get_param = request.env['ir.config_parameter'].sudo().get_param('webhook.url')
        print ('==s==',get_param,kw)
        return {
            'success': True,
            'status': 'OK',
            'webhook': get_param,
            'code': 200
        }
        

    def _get_available_users(self):
        """ get available user of a given channel
            :retuns : return the res.users having their im_status online
        """
        #request.ensure_one()
        #print ('===_get_available_users==',request.env['im_livechat.channel'].sudo().search([], limit=1).user_ids)
        return request.env['mail.channel'].sudo().search([], limit=1).user_ids#.filtered(lambda user: user.im_status == 'online')

    # def _whatsapp_mail_channel(self, senderkeyhash, anonymous_name, previous_operator_id=None, user_id=None, country_id=None):
    #     """ Return a mail.channel given a livechat channel. It creates one with a connected operator, or return false otherwise
    #         :param anonymous_name : the name of the anonymous person of the channel
    #         :param previous_operator_id : partner_id.id of the previous operator that this visitor had in the past
    #         :param user_id : the id of the logged in visitor, if any
    #         :param country_code : the country of the anonymous person of the channel
    #         :type anonymous_name : str
    #         :return : channel header
    #         :rtype : dict

    #         If this visitor already had an operator within the last 7 days (information stored with the 'im_livechat_previous_operator_pid' cookie),
    #         the system will first try to assign that operator if he's available (to improve user experience).
    #     """
    #     #print ('===_whatsapp_mail_channel===',anonymous_name, previous_operator_id, user_id, country_id)
    #     #request.ensure_one()
    #     operator = False
    #     if previous_operator_id:
    #         available_users = self._get_available_users()
    #         # previous_operator_id is the partner_id of the previous operator, need to convert to user
    #         if previous_operator_id in available_users.mapped('partner_id').ids:
    #             operator = next(available_user for available_user in available_users if available_user.partner_id.id == previous_operator_id)
    #     if not operator:
    #         operator = self._get_random_operator()
    #     if not operator:
    #         # no one available
    #         return False

    @http.route('/whatsapp/webhook/', methods=['POST'], type="json", auth="public")
    # @http.route('/webhook/wa/receipt', type='http', auth='none', csrf=False)
    def webhookpost(self, **kwargs):
        data = json.loads(request.httprequest.data)
        if not kwargs:
            return request.make_response(
                data=json.dumps({'error': 'No Data'}),
                headers=[('Content-Type', 'application/json')]
            )
        uuid = kwargs.get('uuid')
        api_key = kwargs.get('x-api-key')
        sender = kwargs.get('sender')
        message = kwargs.get('message')
        senderkeyhash = kwargs.get('senderkeyhash')
        recipientkeyhash = kwargs.get('recipientkeyhash')
        sendername = kwargs.get('sendername')
        value = {
            "uuid": uuid, 
            "x-api-key": api_key, 
            "sender": sender, 
            "messages": message, 
            "sendername": sendername,
            "senderkeyhash": senderkeyhash, 
            "recipientkeyhash": recipientkeyhash,
        }
        # print ('=webhookpost=',data)
        # PublicUser = request.env.user
        # if not request.env.user:
        #     PublicUser = request.env['res.users'].sudo().search([('active','=',False),('login','=','public')], limit=1)
        #     request.env.user = PublicUser
        # Partner = request.env['res.partner'].sudo().search([('whatsapp','=',sender)], limit=1)
        # #print ('===/whatsapp_livechat/get_session=22==',request.env.user)
        # anonymous_name = 'Visitor'
        # if Partner:
        #     anonymous_name = Partner.name
        # user_id = None
        # country_id = None
        # previous_operator_id = None
        # anonymous_name = Partner.name
        # #user_id = PublicUser.id
        # # if Partner:
        # #     Partner = PublicUser.partner_id or False
        # # if the user is identifiy (eg: portal user on the frontend), don't use the anonymous name. The user will be added to session.
        # if request.env.user:
        #     user_id = request.env.user.id
        #     country_id = request.env.user.country_id.id
        # else:
        #     # if geoip, add the country name to the anonymous name
        #     if request.session.geoip:
        #         # get the country of the anonymous person, if any
        #         country_code = request.session.geoip.get('country_code', "")
        #         country = request.env['res.country'].sudo().search([('code', '=', country_code)], limit=1) if country_code else None
        #         if country:
        #             anonymous_name = "%s (%s)" % (anonymous_name, country.name)
        #             country_id = country.id

        # if previous_operator_id:
        #     previous_operator_id = int(previous_operator_id)
        # #channel_id = False
        # MailChannel = request.env['mail.channel'].sudo().search([('uuid','=',uuid),('senderkeyhash', '=', senderkeyhash)], limit=1)
        # #print ('==ActiveMailChannel===',MailChannel)
        # #previous_operator_id = MailChannel.livechat_operator_id
        # # previous_operator_id = self._get_available_users().mapped('partner_id') and self._get_available_users().mapped('partner_id')[0].id
        
        # #Partner = request.env['res.partner'].sudo().search([('whatsapp','=',sender)], limit=1)
        # # anonymous_name = Partner.name
        # #user_id = PublicUser.id
        # if not Partner:
        #     Partner = PublicUser.partner_id or False
        # #print ('=anonymous_name==',anonymous_name)
        # if not MailChannel:
        #     MailChannel = self._whatsapp_mail_channel(senderkeyhash, anonymous_name, previous_operator_id, user_id, country_id)
        #     if not MailChannel:
        #         response_data = {
        #             'error': 'Error',
        #             'user_id': False,
        #         }
        #         #print ('==response_data==',response_data)
        #         return response_data
        #     uuid = MailChannel.uuid
        #print ('==PublicUser===',Partner,MailChannel)
        # MailChannel.message_post(
        #     whatsapp_numbers=sender,
        #     body=message,
        #     message_type='notification',
        #     author_id=Partner.id
        # )
        # return response_data
        account = request.env['ir.whatsapp_server'].sudo().search([('status','=','authenticated')], order='sequence asc', limit=1)

        # if not self._check_signature(account):
        #     raise Forbidden()
        MailChannel = account._process_messages(value)
        response_data = {
            'uuid': MailChannel.uuid,
            # 'user_id': user_id,
        }
        return response_data
        # _logger.warning("Unknown Template webhook : ")
        # for entry in data['entry']:
        #     account_id = entry['id']
        #     account = request.env['whatsapp.account'].sudo().search(
        #         [('account_uid', '=', account_id)])
        #     if not self._check_signature(account):
        #         raise Forbidden()

        #     for changes in entry.get('changes', []):
        #         value = changes['value']
        #         phone_number_id = value.get('metadata', {}).get('phone_number_id', {})
        #         if not phone_number_id:
        #             phone_number_id = value.get('whatsapp_business_api_data', {}).get('phone_number_id', {})
        #         if phone_number_id:
        #             wa_account_id = request.env['whatsapp.account'].sudo().search([
        #                 ('phone_uid', '=', phone_number_id), ('account_uid', '=', account_id)])
        #             if wa_account_id:
        #                 # Process Messages and Status webhooks
        #                 if changes['field'] == 'messages':
        #                     request.env['whatsapp.message']._process_statuses(value)
        #                     wa_account_id._process_messages(value)
        #             else:
        #                 _logger.warning("There is no phone configured for this whatsapp webhook : %s ", data)

        #         # Process Template webhooks
        #         if value.get('message_template_id'):
        #             # There is no user in webhook, so we need to SUPERUSER_ID to write on template object
        #             template = request.env['whatsapp.template'].sudo().search([('wa_template_uid', '=', value['message_template_id'])])
        #             if template:
        #                 if changes['field'] == 'message_template_status_update':
        #                     template.write({'status': value['event'].lower()})
        #                     description = value.get('other_info', {}).get('description', {}) or value.get('reason', {})
        #                     if description:
        #                         template.message_post(
        #                             body=_("Your Template has been rejected.") + Markup("<br/>") + _("Reason : %s", description))
        #                     continue
        #                 if changes['field'] == 'message_template_quality_update':
        #                     template.write({'quality': value['new_quality_score'].lower()})
        #                     continue
        #                 if changes['field'] == 'template_category_update':
        #                     template.write({'template_type': value['new_category'].lower()})
        #                     continue
        #                 _logger.warning("Unknown Template webhook : %s ", value)
        #             else:
        #                 _logger.warning("No Template found for this webhook : %s ", value)

    # @http.route('/whatsapp/webhook/', methods=['GET'], type="http", auth="public", csrf=False)
    # def webhookget(self, **kwargs):
    #     """
    #         This controller is used to verify the webhook.
    #         if challenge is matched then it will make response with challenge.
    #         once it is verified the webhook will be activated.
    #     """
    #     token = kwargs.get('hub.verify_token')
    #     mode = kwargs.get('hub.mode')
    #     challenge = kwargs.get('hub.challenge')
    #     if not (token and mode and challenge):
    #         return Forbidden()
    #     wa_account = request.env['whatsapp.account'].sudo().search([('webhook_verify_token', '=', token)])
    #     if mode == 'subscribe' and wa_account:
    #         response = request.make_response(challenge)
    #         response.status_code = HTTPStatus.OK
    #         return response
    #     response = request.make_response({})
    #     response.status_code = HTTPStatus.FORBIDDEN
    #     return response
