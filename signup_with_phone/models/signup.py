# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import models, api


class ResConfigSettings(models.TransientModel):
    """Inherited res.config.settings for _init_settings function"""

    _inherit = "res.config.settings"

    @api.model
    def _init_settings(self):
        """This method calls when we install module and In this function set
        General setting > Customer Account > Free sign up (B2C)
        And in portal users I have added Employee Rights
        because if Portal user didn't have rights then external users not
        able to to login
        """
        base_settings_obj = self.env["res.config.settings"]
        auth_signup_template_user_id = literal_eval(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("base.template_portal_user_id", "False")
        )
        auth_invitation_scope = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("auth_signup.invitation_scope")
        )
        if auth_invitation_scope != "b2c":
            # Activate allow signup with template user
            base_settings_id = base_settings_obj.create(
                {
                    "auth_signup_uninvited": "b2c",
                    "auth_signup_template_user_id": auth_signup_template_user_id,
                }
            )
            base_settings_id.execute()  # Execute setting
        portal_user_rec = (
            self.env["res.users"]
            .sudo()
            .browse(auth_signup_template_user_id)
            .exists()
        )
        return True
