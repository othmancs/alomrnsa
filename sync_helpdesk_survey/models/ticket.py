# -*- coding: utf-8 -*-
# Part of Synconics. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models


class Ticket(models.Model):
    _name = "ticket.ticket"
    _inherit = ["ticket.ticket", "rating.mixin"]

    def _compute_survey_statistic(self):
        """
        Calculate total survey of ticket
        """
        for rec in self:
            rec.tot_comp_survey = False
            try:
                survey_id = self.env.ref("sync_helpdesk_survey.feedback_form")
            except:
                survey_id = False
            if survey_id:
                rec.tot_comp_survey = survey_id.tot_comp_survey

    @api.depends("rating_ids.rating")
    def _compute_percentage_satisfaction_ticket(self):
        """
        Calculate rating of ticket
        """
        for rec in self:
            rec.percentage_satisfaction_ticket = False
            activity = rec.rating_get_grades()
            if activity:
                rec.percentage_satisfaction_ticket = (
                    activity["great"] * 100 / sum(activity.values())
                    if sum(activity.values())
                    else -1
                )

    def _ticket_count(self):
        """
        Calculate number of survey of ticket
        """
        for ticket in self:
            count_survey = self.env["survey.user_input"].search(
                [("access_token", "=", ticket.survey_token)]
            )
            ticket.count_survey = len(count_survey)

    # survey
    is_email_send = fields.Boolean(string="Survey", copy=False)
    tot_comp_survey = fields.Integer(
        "Number of completed surveys", compute="_compute_survey_statistic"
    )
    survey_token = fields.Char("Token", copy=False)
    count_survey = fields.Integer("Survey Count", compute="_ticket_count", store=False)

    # Rating
    percentage_satisfaction_ticket = fields.Integer(
        compute="_compute_percentage_satisfaction_ticket",
        string="Happy % on Ticket",
        store=True,
        default=-1,
    )
    rating_request_deadline = fields.Datetime(
        compute="_compute_rating_request_deadline", store=True
    )
    rating_status = fields.Selection(
        [
            ("stage", "Rating when changing stage"),
            ("periodic", "Periodical Rating"),
            ("no", "No rating"),
        ],
        "Customer(s) Ratings",
        help="How to get the customer's feedbacks?\n"
        "- Rating when changing stage: Email will be sent when a task/issue is pulled in another stage\n"
        "- Periodical Rating: Email will be sent periodically\n\n"
        "Don't forget to set up the mail templates on the stages for which you want to get the customer's feedbacks.",
        default="no",
        required=True,
        copy=False,
    )
    rating_status_period = fields.Selection(
        [
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("bimonthly", "Twice a Month"),
            ("monthly", "Once a Month"),
            ("quarterly", "Quarterly"),
            ("yearly", "Yearly"),
        ],
        "Rating Frequency",
        copy=False,
    )

    @api.depends("rating_status", "rating_status_period")
    def _compute_rating_request_deadline(self):
        periods = {
            "daily": 1,
            "weekly": 7,
            "bimonthly": 15,
            "monthly": 30,
            "quarterly": 90,
            "yearly": 365,
        }
        for rec in self:
            rec.rating_request_deadline = fields.Datetime.now()
            if rec.rating_status_period:
                rec.rating_request_deadline = fields.Datetime.now() + timedelta(
                    days=periods.get(rec.rating_status_period, 0)
                )

    def write(self, vals):
        """
        Override method for send survey request to customer
        """
        for rec in self:
            if vals.get("stage_id", False):
                stage_id = self.env["ticket.stage"].browse(vals["stage_id"])
                customer_id = self.env["res.partner"].browse(
                    vals.get("partner_id", rec.partner_id.id)
                )
                if (
                    vals.get("is_email_send", rec.is_email_send)
                    and stage_id
                    and stage_id.survey_template
                    and stage_id.is_close
                ):
                    force_send = self.env.context.get("force_send", True)
                    self.rating_send_request(
                        stage_id.survey_template,
                        lang=customer_id.lang,
                        force_send=force_send,
                    )
        return super(Ticket, self).write(vals)

    def partner_survey_count(self):
        """
        Show survey
        """
        self.ensure_one()
        count_surveys = self.env["survey.user_input"].search(
            [("access_token", "=", self.survey_token)]
        )
        tree_view = self.env.ref("survey.survey_user_input_view_tree")
        form_view = self.env.ref("survey.survey_user_input_view_form")
        return {
            "name": "Survey Answer",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "survey.user_input",
            "views": [(tree_view.id, "tree"), (form_view.id, "form")],
            "domain": [("id", "in", count_surveys.ids)],
            "type": "ir.actions.act_window",
            "target": "current",
            "nodestroy": True,
        }

    def default_get_partner(self, user_id):
        if user_id:
            user_id = self.env["res.users"].browse(user_id)
            return user_id.partner_id.id
        return False

    def default_get_survey_token(self, survey):
        if survey:
            survey = self.env["survey.user_input"].browse(survey)
            return survey.access_token
        return False


class TicketStages(models.Model):
    _inherit = "ticket.stage"

    survey_template = fields.Many2one(
        "mail.template",
        domain=[("model_id", "=", "ticket.ticket")],
        string="Feedback Email Template",
    )
