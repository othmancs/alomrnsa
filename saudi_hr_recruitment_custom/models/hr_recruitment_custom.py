# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from datetime import datetime

from dateutil import relativedelta
from lxml import etree
from odoo import _, api, fields, models
from odoo.exceptions import UserError

AVAILABLE_STATES = [
    ("draft", "New"),
    ("cancel", "Refused"),
    ("open", "In Progress"),
    ("pending", "Pending"),
    ("verification", "Verification"),
    ("done", "Hired"),
]


class HrJob(models.Model):
    _name = "hr.job"
    _inherit = ["hr.job", "mail.thread", "mail.activity.mixin"]

    jd_number = fields.Char("JD Number")
    location_id = fields.Many2one("res.partner", string="Location")
    company_number = fields.Char(
        string="Company Number", related="company_id.company_number"
    )
    department_number = fields.Char(
        string="Department Number", related="department_id.department_number"
    )


class ReasonApplicant(models.Model):
    _name = "hr.applicant.hire.reason"
    _description = "Applicant Reason"

    name = fields.Char("Reason")


class ResDocuments(models.Model):
    _inherit = "res.documents"

    applicant_id = fields.Many2one("hr.applicant", "Applicant")


class SurveyUserInput(models.Model):
    """
    Metadata for a set of one user's answers to a particular survey
    """

    _inherit = "survey.user_input"
    _order = "id desc"

    employee_id = fields.Many2one("hr.employee", "Employee")
    applicant_id = fields.Many2one("hr.applicant", "Applicant")


class HrRecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"
    _order = "sequence"

    fold = fields.Boolean(
        "Hide in views if empty",
        help="This stage is not visible, for example in status bar or kanban view, when there are no records in that stage to display.",
    )
    state = fields.Selection(
        AVAILABLE_STATES,
        "Status",
        help="The related status for the stage. The status of your document will automatically change according to the selected stage. Example, a stage is related to the status 'Close', when your document reach this stage, it will be automatically closed.",
    )
    sequence = fields.Integer(
        "Sequence",
        help="Gives the sequence order when displaying a list of stages. Depends on sequence, movement of stages will be restricted. For ex; One can only move from one stage to its next and previous stages.",
    )

    def unlink(self):
        """
        Delete/ remove selected record
        :return: Deleted record ID
        """
        for objects in self:
            if objects.state in ["open", "pending", "verification", "done"]:
                raise UserError(
                    _("You cannot remove the record which is in %s state!")
                    % (objects.state)
                )
        return super(HrRecruitmentStage, self).unlink()


applicant_context = None


class HRApplicant(models.Model):
    _inherit = "hr.applicant"
    _description = "Applicant"
    _order = "id desc"

    def context_data(self):
        global applicant_context
        if applicant_context:
            return applicant_context
        return False

    def unlink(self):
        """
        Delete/ remove selected record
        :return: Deleted record ID
        """
        for objects in self:
            if objects.state in ["open", "pending", "verification", "done"]:
                raise UserError(
                    _("You cannot remove the record which is in %s state!")
                    % objects.state
                )
        return super(HRApplicant, self).unlink()

    partner_name = fields.Char(size=64, required=True, string="Applicant Name")
    marital_status = fields.Selection(
        [
            ("single", "Single"),
            ("married", "Married"),
            ("divorced", "Divorced"),
            ("widower", "Widower"),
        ],
        "Marital Status",
    )
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female")], "Gender", default="male"
    )
    date_action = fields.Datetime("Next Action Date")
    feedback_ids = fields.One2many("hr.survey.feedback", "applicant_id", "Applicant")
    date_of_birth = fields.Date("Date of Birth", required=False)
    is_legal_right = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        "Do you have legal right to work in the country in which you are applying?",
        default="yes",
    )
    join_immedietly = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        "Can you join immediately after your notice period?",
    )
    is_legal_guardianship = fields.Selection(
        [("yes", "Yes"), ("no", "No")], "Do you hold any legal guardianship?"
    )
    national_id = fields.Char("National Id", size=32)
    country_id = fields.Many2one("res.country", "Nationality", required=True)
    is_release = fields.Selection(
        [("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
        "Is your sponsor ready to give release to your company?",
    )
    source_type = fields.Selection(
        [("internal", "Internal"), ("external", "External")],
        "Source Type",
        default="external",
    )
    internal_reference = fields.Many2one("hr.employee", "Referred by")
    not_joining_reason = fields.Text("Reason")

    # To Do
    # visa_id = fields.Many2one('hr.employee.rec.visa', 'Visa')
    joining_date = fields.Date("Joining Date")
    feedback_done = fields.Boolean("Feedback Done", copy=False)
    state = fields.Selection(related="stage_id.state", string="State")
    document_ids = fields.One2many("res.documents", "applicant_id", "Document")
    street = fields.Char("Street", size=128)
    street2 = fields.Char("Street2", size=128)
    zip = fields.Char("Zip", change_default=True, size=24)
    city = fields.Char("City", size=128)
    state_id = fields.Many2one("res.country.state", "State")
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "applicant_attachment_rel",
        "applicant_id",
        "attachment_id",
        "Attachments",
    )
    hired_by = fields.Many2one("res.users", "Hired by", readonly=True, copy=False)
    hired_date = fields.Datetime("Hired on", readonly=True, copy=False)
    refused_by = fields.Many2one("res.users", "Refused by", readonly=True, copy=False)
    refuse_date = fields.Datetime("Refused on", readonly=True, copy=False)
    user_id = fields.Many2one("res.users", "Recruiter")
    emp_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        tracking=True,
        help="Employee linked to the applicant.",
        copy=False,
    )
    is_existing_emp = fields.Boolean(
        string="Is Existing Employee", default=False, copy=False
    )
    existing_employee_id = fields.Many2one(
        "hr.employee", string="Existing Employee", copy=False
    )
    schedule_date = fields.Datetime(string="Schedule Date")
    branch_id = fields.Many2one("hr.branch", string="Location")
    is_hire_not_hire = fields.Selection(
        [("yes", "Yes"), ("no", "No")], string="Hired ?"
    )
    reason_id = fields.Many2one("hr.applicant.hire.reason", string="Reason")

    @api.constrains("date_of_birth")
    def _check_date_of_birth(self):
        """
        Used to check the birthdate
        """
        if self.date_of_birth and self.gender:
            diff = relativedelta.relativedelta(datetime.today(), self.date_of_birth)
            if self.gender == "male" and abs(diff.years) < 18:
                raise UserError(_("Male employee's age must be greater than 18"))
            elif self.gender == "female" and abs(diff.years) < 21:
                raise UserError(_("Female Employee's age must be greater than 21."))

    @api.onchange("is_existing_emp")
    def onchange_existing_emp(self):
        self.existing_employee_id = False

    @api.onchange("existing_employee_id")
    def onchange_existing_employee_id(self):
        if self.existing_employee_id:
            partner_id = self.existing_employee_id.address_home_id
            self.email_from = self.existing_employee_id.private_email or ""
            self.partner_phone = self.existing_employee_id.phone or ""
            self.gender = self.existing_employee_id.gender
            self.date_of_birth = self.existing_employee_id.birthday or False
            self.department_id = (
                self.existing_employee_id.department_id
                and self.existing_employee_id.department_id.id
                or False
            )
            self.job_id = (
                self.existing_employee_id.job_id
                and self.existing_employee_id.job_id.id
                or False
            )

            if partner_id:
                self.partner_mobile = partner_id.mobile
                self.street = partner_id.street
                self.street2 = partner_id.street2
                self.city = partner_id.city
                self.state_id = partner_id.state_id.id
                self.country_id = partner_id.country_id.id
                self.zip = partner_id.zip

    @api.onchange("department_id")
    def onchange_department_id(self):
        """
        Used to set value of job_id and company_id
        """
        requisition_obj = self.env["hr.job.requisition"]
        if self.department_id:
            job_ids = requisition_obj.search(
                [("department_id", "=", self.department_id.id)]
            ).mapped("job_id")
            if job_ids:
                self.job_id = job_ids[0].id
            self.company_id = self.department_id.company_id.id

    @api.onchange("state_id")
    def onchange_state(self):
        """
        Used to set value of country_id based on state
        """
        if self.state_id:
            self.country_id = self.state_id.country_id.id

    @api.onchange("joining_date")
    def onchange_joining_date(self):
        """
        Checks if the joining date is greater than today and provides a warning if it is not.
        :return: {'warning': {'title': 'Information', 'message': 'Joining Date must be greater than
        today'}}
        """
        warning = {}
        if self.joining_date and self.joining_date < datetime.today().date():
            warning.update(
                {
                    "title": _("Information"),
                    "message": _("Joining Date must be greater than today"),
                }
            )
            self.joining_date = False
        return {"warning": warning}

    def case_close_with_emp(self):
        """
        Handles the process of hiring employees, either existing or new, based on job requisitions and applicant details.

        :return: Returns an employee action, which is a dictionary containing information about the action to be performed.
        The dictionary includes the view mode and the resource ID of the employee.
        If `emp_id` is not found, the view mode is set to 'form,tree'.
        """
        state = self.env["hr.recruitment.stage"].search([("state", "=", "done")])
        job_req_pool = self.env["hr.job.requisition"]
        hr_employee = self.env["hr.employee"]
        today = datetime.today()
        emp_id = False
        for applicant in self:
            if applicant.existing_employee_id:
                job_req_obj = job_req_pool.search(
                    [("state", "=", "launch"), ("job_id", "=", self.job_id.id)], limit=1
                )
                if not job_req_obj:
                    raise UserError(
                        _("Kindly define Job Requisition for this job in Launch state.")
                    )
                if job_req_obj.expected_employees == job_req_obj.no_of_employee:
                    raise UserError(
                        _(
                            " Number of hired employee must be less than expected number of employee in recruitment."
                        )
                    )

                applicant.job_id.no_of_hired_employee = (
                    applicant.job_id.no_of_hired_employee + 1
                )

                emp_id = applicant.existing_employee_id
                emp_id.toggle_active()
                emp_id.date_of_join = applicant.joining_date
                emp_id.marital = applicant.marital_status
                emp_id.employee_status = "hired"
                emp_id.job_id = applicant.job_id.id
                emp_id.department_id = applicant.department_id.id
                emp_id.company_id = applicant.company_id.id

                job_requisition_ids = job_req_pool.search(
                    [("state", "=", "launch"), ("job_id", "=", applicant.job_id.id)]
                )
                if job_req_obj:
                    if job_req_obj.expected_employees == job_req_obj.no_of_employee:
                        job_req_obj.state = "done"
                if job_requisition_ids and applicant.job_id.no_of_recruitment <= 1:
                    job_requisition_ids.requisition_done()
                for document_id in applicant.document_ids:
                    document_id.employee_id = emp_id.id
                applicant.write(
                    {
                        "emp_id": emp_id.id,
                        "hired_by": self.env.user.id,
                        "hired_date": today,
                        "stage_id": state.id,
                    }
                )
                job_req_obj.message_post(
                    body=_("Existing Employee %s Hired") % applicant.partner_name
                    if applicant.partner_name
                    else applicant.name,
                    subtype_xmlid="hr_recruitment.mt_job_applicant_hired",
                )
                emp_id.message_post(body=_("Reactive Employee."))
            else:
                address_id = contact_name = False
                if applicant.partner_id:
                    address_id = applicant.partner_id.address_get(["contact"])[
                        "contact"
                    ]
                    contact_name = applicant.partner_id.name_get()[0][1]
                if applicant.job_id and (applicant.partner_name or contact_name):
                    job_req_obj = job_req_pool.search(
                        [("state", "=", "launch"), ("job_id", "=", self.job_id.id)],
                        limit=1,
                    )
                    if not job_req_obj:
                        raise UserError(
                            _(
                                "Kindly define Job Requisition for this job in Launch state."
                            )
                        )
                    if job_req_obj.expected_employees == job_req_obj.no_of_employee:
                        raise UserError(
                            _(
                                " Number of hired employee must be less than expected number of employee in recruitment."
                            )
                        )

                    applicant.job_id.no_of_hired_employee = (
                        applicant.job_id.no_of_hired_employee + 1
                    )

                    emp_id = hr_employee.create(
                        {
                            "name": applicant.partner_name or applicant.name,
                            "job_id": applicant.job_id.id,
                            "company_id": applicant.company_id.id,
                            "address_home_id": address_id,
                            "gender": applicant.gender,
                            "department_id": applicant.department_id.id,
                            "country_id": applicant.country_id.id,
                            "birthday": applicant.date_of_birth,
                            "date_of_join": applicant.joining_date,
                            "marital": applicant.marital_status,
                            "employee_status": "hired",
                        }
                    )

                    if emp_id:
                        applicant.emp_id = emp_id.id
                    job_requisition_ids = job_req_pool.search(
                        [("state", "=", "launch"), ("job_id", "=", applicant.job_id.id)]
                    )
                    if job_req_obj:
                        if job_req_obj.expected_employees == job_req_obj.no_of_employee:
                            job_req_obj.state = "done"
                    if job_requisition_ids and applicant.job_id.no_of_recruitment <= 1:
                        job_requisition_ids.requisition_done()
                    for document_id in applicant.document_ids:
                        document_id.employee_id = emp_id.id
                    applicant.write(
                        {
                            "emp_id": emp_id.id,
                            "hired_by": self.env.user.id,
                            "hired_date": today,
                            "stage_id": state.id,
                        }
                    )
                    job_req_obj.message_post(
                        body=_("New Employee %s Hired") % applicant.partner_name
                        if applicant.partner_name
                        else applicant.name,
                        subtype_xmlid="hr_recruitment.mt_job_applicant_hired",
                    )
                else:
                    raise UserError(
                        _("You must define Applied Job for this applicant.")
                    )
        employee_action = self.env["ir.actions.actions"]._for_xml_id(
            "hr.open_view_employee_list"
        )
        if emp_id:
            employee_action["res_id"] = emp_id.id
        else:
            employee_action["view_mode"] = "form,tree"
        return employee_action

    def view_emp(self):
        """
        Opens a window displaying details of an employee in a new form view.

        :return: The function `view_emp` returns a dictionary `dict_data` containing details to open a
        window displaying the employee data.
        """
        action_id = self.env.ref("hr.view_employee_form", False)
        dict_data = {
            "view_mode": "form",
            "views": [(action_id.id, "form")],
            "view_id": action_id.id,
            "res_id": self.emp_id.id,
            "type": "ir.actions.act_window",
            "res_model": "hr.employee",
            "target": "new",
        }
        return dict_data

    def send_offer_letter(self):
        """
        The function `send_offer_letter` generates a new email message window with predefined template
        and recipient for sending offer letters to job applicants.
        :return: A dictionary containing information for opening a new window to compose an email
        message.
        """
        assert (
            len(self.ids) == 1
        ), "This option should only be used for a single id at a time."
        ir_model_data = self.env["ir.model.data"]
        try:
            template_id = ir_model_data._xmlid_lookup(
                "saudi_hr_recruitment_custom.email_template_applicant_offer"
            )[2]
        except ValueError:
            template_id = False
        compose_form = self.env.ref("mail.email_compose_message_wizard_form", False)
        ctx = self._context.copy()
        ctx.update(
            {
                "default_model": "hr.applicant",
                "default_res_id": self.ids[0],
                "default_use_template": bool(template_id),
                "default_template_id": template_id,
                "default_composition_mode": "comment",
            }
        )
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }

    @api.model_create_multi
    def create(self, vals):
        records = super(HRApplicant, self).create(vals)
        for rec in records:
            template_id = self.env.ref(
                "saudi_hr_recruitment_custom.email_template_create_applicant", False
            )
            if template_id:
                template_id.send_mail(rec.id, force_send=True)
        return records


class HRSurveyFeedback(models.Model):
    _name = "hr.survey.feedback"
    _order = "id desc"
    _rec_name = "stage_id"
    _description = "HR Survey FeedBack"

    applicant_id = fields.Many2one("hr.applicant", "Applicant")
    stage_id = fields.Many2one("hr.recruitment.stage", "Stage", required=True)
    comment = fields.Text("Feedback")
    given_rate = fields.Float("Rate (0-10)")
    feedback_by = fields.Many2one("res.users", "Feedback by")
    next_round_required = fields.Boolean(
        "Next Round Required",
        help="Tick this field if further round required in this stage.",
    )
    employee_id = fields.Many2one(
        "hr.employee",
        "Responsible Person",
        help="Responsible person for next round. A notification mail will be send to this person about next round.",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.user.company_id
    )

    @api.model
    def default_get(self, fields):
        """
        Override method for get default values
        """
        applicant_pool = self.env["hr.applicant"]
        res = super(HRSurveyFeedback, self).default_get(fields)
        applicant_id = self._context.get("active_id", False)
        if applicant_id:
            stage_id = applicant_pool.browse(applicant_id).stage_id.id
            res.update({"stage_id": stage_id})
        return res

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        context = self._context
        res = super(HRSurveyFeedback, self).get_view(view_id, view_type, **options)

        view_type = context.get("is_view", False)
        move_to_next_stage = context.get("move_to_next_stage", False)
        if view_type:
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//separator[@string='Response Information']"):
                if view_type == "feedback":
                    node.set("string", _("Feedback"))
                elif view_type == "refuse":
                    node.set("string", _("Reason of Refusal"))
            for node in doc.xpath("//button[@string='move_to_next_stage']"):
                if view_type == "feedback" and not move_to_next_stage:
                    node.set("string", _("Move to next stage"))
                if view_type == "feedback" and move_to_next_stage:
                    node.set("string", _("Insert Feedback"))
                if view_type == "refuse":
                    node.set("string", _("Refuse"))

            res["arch"] = etree.tostring(doc)
        return res

    @api.onchange("given_rate")
    def onchange_rate(self):
        """
        Checks if a given rate is between 0 and 10 and raises a `UserError` if it is not.
        """
        if self.given_rate and self.given_rate < 0 or self.given_rate > 10:
            raise UserError(_("Please enter rate between 0-10."))

    def feedback_save(self):
        """
        Used to save feedback for a recruitment stage, including handling rating validation,
        sending email reminders, moving to the next stage, and refusing applicants.

        :return: The `feedback_save` method is returning `True` at the end of the function.
        """
        self.ensure_one()
        today = (datetime.today()).strftime("%Y-%m-%d %H:%M:%S")
        stage_pool = self.env["hr.recruitment.stage"]
        applicant_pool = self.env["hr.applicant"]
        applicant_id = self._context.get("active_id", False)
        is_view = self._context.get("is_view", False)
        move_to_next_stage = self._context.get("move_to_next_stage", False)
        for record in self:
            if record.given_rate and record.given_rate < 0 or record.given_rate > 10:
                raise UserError(_("Please enter rate between 0-10."))
            if (
                record.next_round_required
                and record.employee_id
                and is_view != "refuse"
            ):
                template_id = self.env.ref(
                    "saudi_hr_recruitment_custom.email_template_reminder_for_next_round",
                    False,
                )
                if template_id:
                    template_id.send_mail(record.id, force_send=True)
            stage = record.stage_id
            if stage:
                self._cr.execute("""select sequence from hr_recruitment_stage""")
                sequence = [x[0] for x in self._cr.fetchall()]
                sorted_list = sorted(sequence)
                index = sorted_list.index(stage.sequence)
                next_stage = sorted_list[index + 1]
                self.write(
                    {"applicant_id": applicant_id, "feedback_by": self.env.user.id}
                )
                if move_to_next_stage:
                    applicant = applicant_pool.browse(applicant_id)
                    applicant.write({"feedback_done": True})
                if is_view == "feedback" and not move_to_next_stage:
                    stage_id = stage_pool.search([("sequence", "=", next_stage)])
                    for line in stage_id:
                        if line and not record.next_round_required:
                            applicant = applicant_pool.browse(applicant_id)
                            applicant.stage_id = line.id

        if is_view == "refuse":
            stage_id = stage_pool.search([("state", "=", "cancel")])
            if stage_id:
                applicant = applicant_pool.browse(applicant_id)
                applicant.write(
                    {
                        "stage_id": stage_id.id,
                        "refused_by": self.env.user.id,
                        "refuse_date": today,
                    }
                )
            return True
