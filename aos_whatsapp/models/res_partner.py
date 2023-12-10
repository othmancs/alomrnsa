# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, sql_db
from odoo.exceptions import UserError, ValidationError

from odoo.addons.phone_validation.tools import phone_validation
import requests
import json
import re
import time
import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    """Inherit Partner."""
    _inherit = "res.partner"
    
    whatsapp = fields.Char('Whatsapp', default='0')
    whatsapp_type = fields.Selection([('@c.us','Contact'),('@g.us','Group')], string='Whatsapp Type')
    chat_id = fields.Char(string='ChatID')
    
    def send_whatsapp(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.compose.message',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_user_id': self.id},
        }

    def _formatting_mobile_number(self):
        for rec in self:
            module_rec = self.env['ir.module.module'].sudo().search_count([
                ('name', '=', 'crm_phone_validation'),
                ('state', '=', 'installed')])
            country_code = str(rec.country_id.phone_code) if rec.country_id else str(self.company_id.country_id.phone_code)
            country_count = len(str(rec.country_id.phone_code))
            whatsapp_number = rec.whatsapp
            if rec.whatsapp[:country_count] == str(rec.country_id.phone_code):
                whatsapp_number = rec.whatsapp
                # print ('==whatsapp_number=11=',whatsapp_number)
            elif rec.whatsapp[0] == '0':
                if rec.whatsapp[1:country_count+1] == str(rec.country_id.phone_code):
                    #COUNTRY CODE UDH DIDEPAN
                    whatsapp_number = rec.whatsapp[1:]
                else:
                    whatsapp_number = country_code + rec.whatsapp[1:]
                # print ('==whatsapp_number=22=',whatsapp_number)
                # print ('==whatsapp_number==',whatsapp_number)
            return whatsapp_number
            #if rec.whatsapp == len
            # return module_rec and re.sub("[^0-9]", '', rec.whatsapp) or \
            #     country_code + rec.whatsapp[1:] if rec.whatsapp[0] == '0' else country_code + rec.whatsapp
            # # return module_rec and re.sub("[^0-9]", '', rec.whatsapp) or \
            #     str(rec.country_id.phone_code
            #         ) + rec.whatsapp[1:] if rec.whatsapp[0] == '0' else rec.whatsapp

    @api.constrains('whatsapp')
    def _validate_mobile(self):
        for rec in self:
            whatsapp = rec._formatting_mobile_number()
            if not whatsapp.isdigit():
                raise ValidationError(_("Invalid whatsapp number."))

    def check_whatsapp_number_response(self, whatsapp_ids):
        """Method to check mobile is on whatsapp."""
        number_dict = {}
        if self.whatsapp:
            whatsapp = self._formatting_mobile_number()
            KlikApi = whatsapp_ids.klikapi()
            number_dict = KlikApi.get_phone(method='checkPhone', phone=whatsapp)
        return number_dict

    def check_number_whatsapp(self):
        """Check Partner Mobile."""
        WhatsappServer = self.env['ir.whatsapp_server']
        whatsapp_ids = WhatsappServer.search([('status','=','authenticated')], order='sequence asc')
        for rec in self:
            if len(whatsapp_ids) == 1:
                KlikApi = whatsapp_ids.klikapi()
                KlikApi.auth()
                numbers = rec.check_whatsapp_number_response(whatsapp_ids)
                #print ('==company_id==',company_id,number_dict,rec.name,rec.mobile)
                if rec.name and rec.whatsapp and numbers.get('error'):
                    _logger.warning(_('Error: ' + rec.name + ' with number ' + rec.whatsapp +' '+numbers.get('error')))
                    #raise UserError(_(rec.name + ' with number ' + rec.whatsapp +' '+number_dict.get('error')))
                if numbers.get('result') == 'not exists':
                    _logger.warning('Failed added WhatsApp number ', rec.whatsapp)
                elif numbers.get('result') == 'exists':
                    rec.whatsapp_type = '@c.us'
                    _logger.warning('Success added WhatsApp number ', rec.whatsapp)

    def _find_or_create_from_number(self, number, name=False):
        """ Number should come currently from whatsapp and contain country info. """
        number_with_sign = '+' + number
        format_number = phone_validation.phone_format(number_with_sign, False, False)
        number_country_code = int(phone_validation.phone_parse(format_number, None).country_code)
        country = self.env['res.country'].search([('phone_code', '=', number_country_code)])
        if not number and not format_number:
            return self.env['res.partner']
        partner = self.env['res.partner'].search(
            ['|', ('mobile', '=', format_number), ('phone', '=', format_number)],
            limit=1
        )
        if not partner:
            partner = self.env['res.partner'].create({
                'name': name or format_number,
                'mobile': format_number,
                'country_id': country.id if country else False,
            })
            partner._message_log(
                body=_("Partner created by incoming WhatsApp message.")
            )
        return partner
