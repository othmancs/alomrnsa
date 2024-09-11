# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import fields, models


class HrRecruitmentResumeLine(models.Model):
    _name = "hr.recruitment.resume.line"
    _description = "Resume line of an employee"
    _order = "line_type_id, date_end desc, date_start desc"

    employee_id = fields.Many2one("hr.employee", ondelete="cascade")
    applicant_id = fields.Many2one("hr.applicant")
    name = fields.Char(required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date()
    description = fields.Text(string="Description")
    line_type_id = fields.Many2one("hr.resume.line.type", string="Type")

    # Used to apply specific template on a line
    display_type = fields.Selection(
        [("classic", "Classic")], string="Display Type", default="classic"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("refuse", "Refused"), ("approve", "Approved")],
        "Status",
        readonly=1,
        default="draft",
    )
    type_code = fields.Char(related="line_type_id.code", readonly=True)
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

    _sql_constraints = [
        (
            "date_check",
            "CHECK ((date_start <= date_end OR date_end = NULL))",
            "The start date must be anterior to the end date.",
        ),
    ]

    def action_send_mail(self):
        """
        Sent an email using email template
        """
        template_id = self.env.ref(
            "hr_skills_recruitment.recruitment_email_template_employment_reference",
            False,
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
        for experience in self:
            experience.state = "approve"

    def experience_refuse(self):
        """
        Set the refuse state
        """
        for experience in self:
            experience.state = "refuse"

    def check_certificate_expiry(self):
        template_id = self.env.ref(
            "hr_skills_recruitment.resume_cerificate_expiry_notification", False
        )
        if template_id:
            for certificate in self.search([]):
                if certificate.date_end:
                    notification_date = certificate.date_end - relativedelta(days=+10)
                    if fields.Date.today() == notification_date:
                        template_id.send_mail(certificate.id, force_send=True)


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    resume_line_ids = fields.One2many(
        "hr.recruitment.resume.line", "applicant_id", string="Resumé lines"
    )
    employee_skill_ids = fields.One2many(
        "hr.recruitment.employee.skill", "applicant_id", string="Skills"
    )

    def case_close_with_emp(self):
        rec = super(HrApplicant, self).case_close_with_emp()
        if self.emp_id:
            for line in self.resume_line_ids:
                self.env["hr.resume.line"].create(
                    {
                        "employee_id": self.emp_id.id or False,
                        "state": line.state,
                        "is_current_job": line.is_current_job or False,
                        "company": line.company or False,
                        "job_title": line.job_title or False,
                        "location": line.location or False,
                        "contact_name": line.contact_name or False,
                        "contact_phone": line.contact_phone or False,
                        "contact_email": line.contact_email or False,
                        "contact_title": line.contact_title or False,
                        "organization_name": line.organization_name or False,
                        "certification_month": line.certification_month or False,
                        "certification_year": line.certification_year or False,
                        "reg_no": line.reg_no or False,
                        "degree_id": line.degree_id.id or False,
                        "university_id": line.university_id or False,
                        "completion_year": line.completion_year or False,
                        "completion_month": line.completion_month or False,
                        "field_of_study": line.field_of_study or False,
                        "grade": line.grade or False,
                        "activities": line.activities or False,
                        "percentage": line.percentage or False,
                        "name": line.name or False,
                        "date_start": line.date_start or False,
                        "date_end": line.date_end or False,
                        "description": line.description or False,
                        "line_type_id": line.line_type_id.id or False,
                    }
                )
            for skill in self.employee_skill_ids:
                self.env["hr.employee.skill"].create(
                    {
                        "employee_id": self.emp_id.id,
                        "skill_id": skill.skill_id.id or False,
                        "skill_level_id": skill.skill_level_id.id or False,
                        "skill_type_id": skill.skill_type_id.id or False,
                        "level_progress": skill.level_progress or False,
                    }
                )
        return rec
