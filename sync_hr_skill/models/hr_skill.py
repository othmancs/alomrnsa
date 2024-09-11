# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import fields, models


class ResumeLine(models.Model):
    _inherit = "hr.resume.line"

    state = fields.Selection(
        [("draft", "Draft"), ("refuse", "Refused"), ("approve", "Approved")],
        "Status",
        readonly=1,
        default="draft",
    )
    type_code = fields.Char(related="line_type_id.code", readonly=True)
    applicant_id = fields.Many2one("hr.applicant")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )

    # Experience Fields
    is_current_job = fields.Selection([("yes", "Yes"), ("no", "No")], "Current Job")
    company = fields.Char("Company Name", size=128)
    job_title = fields.Char("Job Title", size=128)
    location = fields.Char("Location", size=64)
    contact_name = fields.Char("Contact Name", size=64)
    contact_phone = fields.Char("Contact Phone No", size=20)
    contact_email = fields.Char("Contact Email", size=64)
    contact_title = fields.Char("Contact Title", size=24)

    # Certification Fields
    organization_name = fields.Char("Issuing Organization")
    certification_month = fields.Selection(
        [
            ("1", "January"),
            ("2", "February"),
            ("3", "March"),
            ("4", "April"),
            ("5", "May"),
            ("6", "June"),
            ("7", "July"),
            ("8", "August"),
            ("9", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        string="Month",
    )
    certification_year = fields.Char(string="Year")
    reg_no = fields.Char("Registration No.")

    # Qualification Fields
    degree_id = fields.Many2one("hr.recruitment.degree", "Program")
    university_id = fields.Char("University Name", size=64)
    completion_year = fields.Char(string="Year")
    completion_month = fields.Selection(
        [
            ("1", "January"),
            ("2", "February"),
            ("3", "March"),
            ("4", "April"),
            ("5", "May"),
            ("6", "June"),
            ("7", "July"),
            ("8", "August"),
            ("9", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        string="Month",
    )
    field_of_study = fields.Char("Field of Study", size=64)
    grade = fields.Float("Grade(GPA)")
    activities = fields.Text("Activities and Societies")
    percentage = fields.Float(string="Percentage")

    def action_send_mail(self):
        """
        Sends an email using a specified email template.

        :return: An action to send an email using an email template is being returned. The function
        prepares the context with default values for the email composition, such as the template to use
        and the mode of composition. Finally, it returns an action window to open a form for composing
        the email with the provided context.
        """
        template_id = self.env.ref(
            "sync_hr_skill.email_template_employment_reference", False
        )
        compose_form_id = self.env.ref("mail.email_compose_message_wizard_form", False)

        ctx = self._context.copy()
        ctx.update(
            {
                "default_res_id": self.id,
                "default_use_template": bool(template_id),
                "default_template_id": template_id.id or False,
                "default_composition_mode": "comment",
            }
        )
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id.id, "form")],
            "view_id": compose_form_id.id,
            "target": "new",
            "context": ctx,
        }

    def experience_approve(self):
        """
        Set the approve state
        """
        for expirence in self:
            expirence.state = "approve"

    def experience_refuse(self):
        """
        Set the refuse state
        """
        for expirence in self:
            expirence.state = "refuse"

    def check_certificate_expiry(self):
        try:
            template_id = self.env.ref("sync_hr_skill.cerificate_expiry_notification")
        except ValueError:
            template_id = False
        for certificate in self.search([]):
            if certificate.date_end:
                notification_date = certificate.date_end - relativedelta(days=+10)
                if fields.Date.today() == notification_date:
                    template_id.send_mail(certificate.id, force_send=True)


class ResumeLineType(models.Model):
    _inherit = "hr.resume.line.type"

    code = fields.Char(string="Code", required=True)

    _sql_constraints = [
        (
            "code_uniq",
            "unique (code)",
            "The code of the resume line type must be unique!",
        )
    ]
