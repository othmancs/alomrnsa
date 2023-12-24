# -*- coding: utf-8 -*-

import werkzeug
import logging

from odoo.http import request
from odoo import http, _
from odoo.exceptions import UserError

from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.auth_signup.controllers.main import (
    ensure_db,
    AuthSignupHome as Home,
)
from odoo.addons.web.controllers.main import SIGN_UP_REQUEST_PARAMS

_logger = logging.getLogger(__name__)

SIGN_UP_REQUEST_PARAMS.add("mobile_login")


class AuthSignupHome(Home):
    @http.route(
        "/web/signup", type="http", auth="public", website=True, sitemap=False
    )
    def web_auth_signup(self, *args, **kw):
        """Override router to add Email/Mobile Validation."""
        qcontext = self.get_auth_signup_qcontext()
        qcontext["mobile_field"] = kw.get("mobile_field") and True or False
        if not qcontext.get("token") and not qcontext.get("signup_enabled"):
            raise werkzeug.exceptions.NotFound()
        if "error" not in qcontext and request.httprequest.method == "POST":
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get("token"):
                    User = request.env["res.users"]
                    user_sudo = User.sudo().search(
                        User._get_login_domain(qcontext.get("login")),
                        order=User._get_login_order(),
                        limit=1,
                    )
                    template = request.env.ref(
                        "auth_signup.mail_template_user_signup_account_created",
                        raise_if_not_found=False,
                    )
                    if user_sudo and template:
                        template.sudo().send_mail(
                            user_sudo.id, force_send=True
                        )
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext["error"] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if (
                    request.env["res.users"]
                    .sudo()
                    .search([("login", "=", qcontext.get("login"))])
                ):
                    qcontext["error"] = _(
                        "Another user is already registered using this email address/Mobile Number."
                    )
                else:
                    # Raise Error for Email/Mobile not available.
                    if not qcontext["login"] and not qcontext["mobile"]:
                        _logger.error(e.message)
                        qcontext["error"] = _("Please Enter Email or Mobile.")
                    else:
                        _logger.error("%s", e)
                        qcontext["error"] = _(
                            "Could not create a new account."
                        )

        response = request.render("auth_signup.signup", qcontext)
        response.headers["X-Frame-Options"] = "DENY"
        return response

    def _prepare_signup_values(self, qcontext):
        """Create User & Partner with Extra field Mobile."""
        values = super(AuthSignupHome, self)._prepare_signup_values(qcontext)
        _find_partner = (
            lambda login: request.env["res.partner"]
            .sudo()
            .search([("email", "=", login)])
        )
        if _find_partner(qcontext.get("login")) or _find_partner(
            qcontext.get("email")
        ):
            raise UserError(
                _("A user is already registered using this email address.")
            )
        if qcontext.get("login"):
            values.update(dict(mobile=qcontext.get("login")))
        if qcontext.get("email"):
            values.update(dict(email=qcontext.get("email")))
        return values

    @http.route("/web/login", type="http", auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        res = super(AuthSignupHome, self).web_login(redirect, **kw)
        if (
            "mobile" in request.params
            and "login_success" in request.params
            and request.params.get("mobile")
            and not request.params.get("login_success")
        ):
            res.qcontext.update({"mobile_login": "true"})
        return res
