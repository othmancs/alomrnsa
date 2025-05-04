from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class SoundController(http.Controller):
    @http.route("/sound_alert/<int:alert_id>", methods=["POST"], type="json", auth="none")
    def generate_sound_alert(self, alert_id, **kw):
        """
        This method is created to allow external services hit the controller and generate sound.
        But this function has left the authentication process upto the developer, developer can perform
        the authentication of user by hiw own custom logic.

        :param alert_id: <int: alert record id>
        :param kw: {
                        "params": {
                            "partner_id": 3,
                            "partner_ids": [2,3]
                        }
                    }
        :return: None
        """

        self.authenticate_user()
        alert_rec = request.env["sound_alert.alerts"].browse(alert_id)
        if not alert_rec:
            _logger.warning("No Alert Record with the id: %s present in the system!", alert_id)
        else:
            params = {
                'sound_stream': alert_rec.sound_alert_binary if alert_rec.alert_type == 'sound' else alert_rec.voice_alert_binary
            }
            if kw.get('partner_id', False):
                request.env['bus.bus']._sendone(request.env['res.partner'].browse(kw.get("partner_id")), 'voice_alert_sound', params)
            if kw.get("partner_ids", []):
                notifications = [[x, 'voice_alert_sound', params] for x in request.env['res.partner'].browse(kw.get("partner_ids"))]
                request.env['bus.bus']._sendmany(notifications)

    def authenticate_user(self):
        """
        Over-ride this method and add your own custom logic to authenticate the user.
        """
        pass
