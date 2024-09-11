# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models


class HrQualification(models.Model):
    _name = "hr.qualification"
    _description = "HR Qualification"

    employee_id = fields.Many2one("hr.employee", "Employee")
    degree_id = fields.Many2one("hr.recruitment.degree", "Program", required=True)
    university_id = fields.Char("University Name", size=64)
    attended_date_from = fields.Date("Dates Attended(from)")
    attended_date_to = fields.Date("Dates Attended(to)")
    program_type = fields.Selection(
        [("completed", "Completed"), ("ongoing", "Ongoing")],
        "Program Status",
        required=True,
    )
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
    description = fields.Text("Description")
    contact_name = fields.Char("Contact Name", size=64)
    contact_phone = fields.Char("Contact Phone No", size=32)
    contact_email = fields.Char("Contact Email", size=64)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    percentage = fields.Float(string="Percentage")

    @api.depends("employee_id")
    def name_get(self):
        """
        To use retrieving the employee name
        """
        res = []
        for rec in self:
            if rec.employee_id:
                name = "".join(
                    [
                        rec.employee_id.name,
                        " - ",
                        rec.degree_id.name,
                        " - Qualification",
                    ]
                )
            else:
                name = "".join([rec.degree_id.name, " - Qualification"])
            res.append((rec.id, name))
        return res


class HrCertification(models.Model):
    _name = "hr.certification"
    _description = "HR Certification"

    employee_id = fields.Many2one("hr.employee", "Employee")
    name = fields.Char("Certification Name", required=True)
    organization_name = fields.Char("Issuing Organization", required=True)
    issue_date = fields.Date("Date of Issue")
    expiry_date = fields.Date("Date of Expiry")
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
    contact_name = fields.Char("Contact Name", size=64)
    contact_phone = fields.Char("Contact Phone No", size=32)
    contact_email = fields.Char("Contact Email", size=64)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )

    def check_certificate_expiry(self):
        try:
            template_id = self.env.ref(
                "saudi_hr_exp_info.cerificate_expiry_notification"
            )
        except ValueError:
            template_id = False
        for certificate in self.search([]):
            notification_date = certificate.expiry_date - relativedelta(days=+10)
            if fields.Date.today() == notification_date:
                template_id.send_mail(certificate.id, force_send=True)


class HrExperience(models.Model):
    _name = "hr.experience"
    _description = "HR Experience"

    is_current_job = fields.Selection([("yes", "Yes"), ("no", "No")], "Current Job")
    employee_id = fields.Many2one("hr.employee", "Employee")
    company = fields.Char("Company Name", size=128, required=True)
    job_title = fields.Char("Job Title", size=128, required=True)
    location = fields.Char("Location", size=64)
    time_period_from = fields.Date("Time Period(from)", required=True)
    time_period_to = fields.Date("Time Period(to)")
    description = fields.Text("Description")
    contact_name = fields.Char("Contact Name", size=64, required=True)
    contact_phone = fields.Char("Contact Phone No", size=20)
    contact_email = fields.Char("Contact Email", size=64, required=True)
    contact_title = fields.Char("Contact Title", size=24)
    state = fields.Selection(
        [("draft", "Draft"), ("refuse", "Refused"), ("approve", "Approved")],
        "Status",
        readonly=1,
        default="draft",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )

    @api.depends("employee_id")
    def name_get(self):
        """
        To use retrieving the employee name
        """
        res = []
        for rec in self:
            if rec.employee_id:
                name = "".join(
                    [rec.employee_id.name, " - ", rec.company, " - Experience"]
                )
            else:
                name = "".join([rec.company, " - Experience"])
            res.append((rec.id, name))
        return res

    def action_send_mail(self):
        """
        Sent an email using email template
        """
        template_id = self.env.ref(
            "saudi_hr_exp_info.email_template_employment_reference", False
        )
        compose_form_id = self.env.ref("mail.email_compose_message_wizard_form", False)
        ctx = self._context.copy()
        ctx.update(
            {
                "default_model": "hr.experience",
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
