# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug
from odoo import _, http
from odoo.addons.rating.controllers.main import Rating
from odoo.addons.survey.controllers.main import Survey
from odoo.exceptions import UserError
from odoo.http import request


class RatingHelpdesk(Rating):
    @http.route(
        ["/rating/<string:token>/<int:rate>/submit_survey"],
        type="http",
        auth="public",
        method=["post"],
    )
    def submit_survey(self, token, rate, **kwargs):
        """
        Submits a survey response based on a given token and rating, and redirects the user to a survey form URL.

        :param token: Used to identify a specific rating record in the database.
        It is used to search for a rating record based on the access token provided
        :param rate: Used to specify the rating that will be applied to a particular record.
        It is a numerical value representing the rating given by a user for a specific item or service.
        :return: Returning a redirection to a public survey URL if certain conditions are met.
        """
        rating = (
            request.env["rating.rating"].sudo().search([("access_token", "=", token)])
        )
        if not rating:
            return request.not_found()
        record_sudo = request.env[rating.res_model].sudo().browse(rating.res_id)
        record_sudo.rating_apply(rate, token=token, feedback=kwargs.get("feedback"))
        ticket_id = request.env["ticket.ticket"].sudo().browse(rating.res_id)
        stage_id = ticket_id.stage_id.sudo()
        if ticket_id and stage_id and stage_id.survey_template and stage_id.is_close:
            base_url = (
                "/"
                if request.env.context.get("relative_url")
                else request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            survey_id = request.env.ref("sync_helpdesk_survey.feedback_form")
            survey_sudo = survey_id.sudo()
            answer_sudo = (
                request.env["survey.user_input"]
                .sudo()
                .search(
                    [
                        ("survey_id", "=", survey_sudo.id),
                        ("access_token", "=", ticket_id.survey_token),
                    ],
                    limit=1,
                )
            )
            if not answer_sudo:
                try:
                    answer_sudo = survey_sudo._create_answer(
                        user=request.env.user, email=ticket_id.partner_email
                    )
                except UserError:
                    answer_sudo = False
            public_url = werkzeug.urls.url_join(
                base_url,
                "survey/start/%s?answer_token=%s"
                % (survey_sudo.access_token, answer_sudo.access_token),
            )
            request.session["ticket_id"] = ticket_id.id
            if public_url:
                return werkzeug.utils.redirect(public_url)


class Survey(Survey):
    @http.route(
        "/survey/start/<string:survey_token>", type="http", auth="public", website=True
    )
    def survey_start(self, survey_token, answer_token=None, email=False, **post):
        """
        Handles the initiation of a survey, updating a ticket's survey token if provided.

        :param survey_token: Used to identify a specific survey within the `survey_start` method.
        It is passed as an argument when calling the `survey_start` method and is used to retrieve
        or update information related to that particular survey
        :param answer_token: Used to pass a token that identifies the answer or response associated
        with a survey. It is used to link the survey response to a specific user or session.
        In the provided code snippet, if the `answer_token` is provided as
        :param email: Boolean flag that indicates whether an email should be sent.
        If `email` is set to `True`, it means that an email will be sent as part of the survey process.
        If `email` is set to `False`,, defaults to False (optional)
        """
        if answer_token:
            res = super(Survey, self).survey_start(
                survey_token=survey_token,
                answer_token=answer_token,
                email=email,
                **post
            )
            ticket_id = (
                request.env["ticket.ticket"].sudo().browse(request.session.ticket_id)
            )
            if answer_token and ticket_id:
                ticket_id.write({"survey_token": answer_token})
        else:
            answer_token = request.httprequest.cookies.get("survey_%s" % survey_token)
            if answer_token and ticket_id:
                ticket_id.write({"survey_token": answer_token})
        return res
