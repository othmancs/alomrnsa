# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import base64
from datetime import datetime
from io import BytesIO

import xlsxwriter
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class InterviewLogReport(models.TransientModel):
    _name = "interview.log.reports"
    _description = "Interview Log Report"

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    @api.model
    def default_get(self, default_fields):
        """
        Overrides the default values for fields `start_date` and `end_date`
        in the `InterviewLogReport` class.

        :param default_fields: List of field names for which default values need to be retrieved.
        :return: Returns a dictionary `res` that contains default values for the fields `start_date`
        and `end_date`. The `start_date` is set to the first day of the current month, and the
        `end_date` is set to the last day of the current month.
        """
        res = super(InterviewLogReport, self).default_get(default_fields)
        res.update(
            {
                "start_date": fields.Date.today() + relativedelta(day=1),
                "end_date": fields.Date.today()
                + relativedelta(day=1, months=+1, days=-1),
            }
        )
        return res

    def generate_interview_log_pdf_report(self):
        """
        Generates a PDF report for an interview log using data from the environment.

        :return: Returns the result of calling the `report_action` method on the reference
        to the report template 'action_report_interview_log', passing in the `data` obtained
        from reading the data.
        """
        data = self.read()[0]
        return self.env.ref(
            "saudi_hr_recruitment_custom.action_report_interview_log"
        ).report_action(self, data=data)

    def action_view_reports(self):
        applicant_ids = self.env["hr.applicant"].search([])
        applicant_ids = applicant_ids.filtered(
            lambda a: a.create_date.date() >= self.start_date
            and a.create_date.date() <= self.end_date
        )
        tree_view = self.env.ref("hr_recruitment.crm_case_tree_view_job")
        if applicant_ids:
            return {
                "type": "ir.actions.act_window",
                "name": _("Interview Log"),
                "res_model": "hr.applicant",
                "view_mode": "tree",
                "views": [(tree_view.id, "tree")],
                "domain": [("id", "in", applicant_ids.ids)],
            }
        else:
            raise ValidationError(_("No Record Found!"))

    def generate_interview_log_excel_report(self):
        """
        Generates an Excel report of interview logs based on specified criteria and returns
        a download link for the generated file.

        :return: Returns a dictionary containing information for downloading the Excel report generated.
        """
        filename = "InterviewLog.xlsx"
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet("Interview Log")
        worksheet.set_column("A:B", 15)
        worksheet.set_column("B:C", 20)
        worksheet.set_column("D:D", 15)
        worksheet.set_column("E:E", 30)
        worksheet.set_column("F:F", 10)
        worksheet.set_column("G:G", 40)

        heading_title = workbook.add_format(
            {
                "bold": 1,
                "font_size": 18,
                "align": "center",
                "font_name": "Times New Roman",
                "text_wrap": True,
                "border": 2,
            }
        )
        heading = workbook.add_format(
            {
                "bold": 1,
                "font_size": 15,
                "align": "center",
                "font_name": "Times New Roman",
                "text_wrap": True,
            }
        )
        content = workbook.add_format(
            {
                "font_size": 15,
                "align": "center",
                "font_name": "Times New Roman",
                "text_wrap": True,
            }
        )

        col = 0
        row = 1
        worksheet.merge_range(row, 0, row + 1, 6, "Interview Log Report", heading_title)
        row = 4
        worksheet.write(row, col, "NAME", heading)
        worksheet.write(row, col + 1, "DATE APPLIED", heading)
        worksheet.write(row, col + 2, "SCHEDULED INTERVIEW", heading)
        worksheet.write(row, col + 3, "LOCATION", heading)
        worksheet.write(row, col + 4, "POSITION", heading)
        worksheet.write(row, col + 5, "YES/NO", heading)
        worksheet.write(row, col + 6, "REASON", heading)
        row += 1

        applicant_ids = self.env["hr.applicant"].search([])
        for applicant in applicant_ids.filtered(
            lambda a: a.create_date.date() >= self.start_date
            and a.create_date.date() <= self.end_date
        ):
            create_date = (
                datetime.strftime(applicant.create_date, "%d %b %y")
                if applicant.create_date
                else ""
            )
            schedule_date = (
                datetime.strftime(applicant.schedule_date, "%d %b %y")
                if applicant.schedule_date
                else ""
            )

            hire = ""
            if applicant.is_hire_not_hire == "yes":
                hire = "Yes"
            if applicant.is_hire_not_hire == "no":
                hire = "No"

            worksheet.write(row, col, applicant.partner_name or "", content)
            worksheet.write(row, col + 1, create_date, content)
            worksheet.write(row, col + 2, schedule_date, content)
            worksheet.write(row, col + 3, applicant.branch_id.name or "", content)
            worksheet.write(row, col + 4, applicant.job_id.name or "", content)
            worksheet.write(row, col + 5, hire or "", content)
            worksheet.write(row, col + 6, applicant.reason_id.name or "", content)
            row += 1

        workbook.close()
        result = base64.encodebytes(fp.getvalue())
        fp.close()
        excel_file = self.env["ir.attachment"].create(
            {
                "name": filename,
                "datas": result,
                "res_model": "interview.log.reports",
                "res_id": self.id,
                "type": "binary",
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % (excel_file.id),
            "target": "new",
            "nodestroy": False,
        }
