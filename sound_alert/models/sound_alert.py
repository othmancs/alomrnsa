# -*- coding: utf-8 -*-
import base64
import io

import gtts
from odoo import models, fields, api


class SoundAlert(models.Model):
    _name = 'sound_alert.alerts'
    _description = 'Sound Alerts'

    name = fields.Char(string="Alert Name", required=True)
    alert_type = fields.Selection(selection=[("sound", "Sound"), ("voice", "Voice")], string="Alert Type",
                                  required=True)

    # Sound Alert Options
    sound_alert_binary = fields.Binary(attachment=True, string="Audio File (mp3)")

    # Voice Alert Options
    voice_alert_text = fields.Text(string="Voice Alert Text", default="This is Alert!")
    voice_alert_binary = fields.Binary(attachment=True, string="Voice Audio File")

    # computed fields
    python_model_text = fields.Char(compute="get_python_model_text")
    api_admin_user_demo_text = fields.Char(compute="get_api_admin_user_demo_text")
    api_admin_demo_user_demo_text = fields.Char(compute="get_api_admin_demo_user_demo_text")
    api_admin_custom_text_demo_text = fields.Char(compute="get_api_admin_custom_text_demo_text")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SoundAlert, self).create(vals_list)
        for rec in res:
            if rec.alert_type == 'voice' and rec.voice_alert_text:
                rec.update_voice_binary_file()
        return res

    def write(self, data):
        res = super(SoundAlert, self).write(data)
        if (any(['alert_type' in data, 'voice_alert_text' in data]) and self.alert_type == 'voice'
                and self.voice_alert_text):
            self.update_voice_binary_file()
        return res

    def update_voice_binary_file(self):
        file_obj = self.get_voice_binary_file(self.voice_alert_text)
        self.write({'voice_alert_binary': file_obj.read()})

    def get_voice_binary_file(self, voice_alert_text):
        sound_byte = gtts.gTTS(voice_alert_text)
        file_obj = io.BytesIO()
        for idx, decoded in enumerate(sound_byte.stream()):
            file_obj.write(base64.b64encode(decoded))
        file_obj.seek(0)
        return file_obj

    def generate_alert(self):
        return {
            'type': 'ir.actions.client',
            'tag': "generate_sound_alert",
            'params': {
                'sound_stream': self.sound_alert_binary if self.alert_type == 'sound' else self.voice_alert_binary,
            }
        }

    @api.model
    def generate_sound_by_id(self, id):
        rec_id = self.browse(id)
        return rec_id.generate_alert()

    @api.model
    def generate_sound_to_partners(self, alert_rec_id=0, partner_id=0, partner_ids=(), custom_voice_text=""):
        alert_rec = self.browse(alert_rec_id)
        params = {}
        if alert_rec:
            params[
                'sound_stream'] = alert_rec.sound_alert_binary if alert_rec.alert_type == 'sound' else alert_rec.voice_alert_binary
        elif custom_voice_text:
            params['sound_stream'] = self.get_voice_binary_file(custom_voice_text).read()
        else:
            return

        if partner_id:
            partner_rec_id = self.env['res.partner'].browse(partner_id)
            self.env['bus.bus'].sudo()._sendone(partner_rec_id, 'voice_alert_sound', params)
        if partner_ids:
            partner_rec_ids = self.env['res.partner'].browse(partner_ids)
            notifications = [[x, 'voice_alert_sound', params] for x in partner_rec_ids]
            self.env['bus.bus'].sudo()._sendmany(notifications)

    def get_python_model_text(self):
        self.python_model_text = "return self.env['sound_alert.alerts'].generate_sound_by_id(%s)" % self.id

    def get_api_admin_user_demo_text(self):
        self.api_admin_user_demo_text = "self.env['sound_alert.alerts'].generate_sound_to_partners(alert_rec_id=%s, partner_id=%s)" % (
            self.id, self.env.ref('base.user_admin').partner_id.id)

    def get_api_admin_demo_user_demo_text(self):
        self.api_admin_demo_user_demo_text = "self.env['sound_alert.alerts'].generate_sound_to_partners(alert_rec_id=%s, partner_ids=(%s, %s))" % (
            self.id, self.env.ref('base.user_admin').partner_id.id, self.env.ref('base.user_demo').partner_id.id)

    def get_api_admin_custom_text_demo_text(self):
        self.api_admin_custom_text_demo_text = "self.env['sound_alert.alerts'].generate_sound_to_partners(partner_id=%s, custom_voice_text='This is Sample Voice Message!')" % self.env.ref(
            'base.user_admin').partner_id.id
