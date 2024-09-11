# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import base64
from io import BytesIO

import xlsxwriter
from odoo import fields, models
from xlsxwriter.utility import xl_rowcol_to_cell


class ManpowerReport(models.TransientModel):
    _name = "manpower.report"
    _description = "Manpower Report"

    fiscal_year_id = fields.Many2one("year.year", "Manpower Plan Year", required=True)
    filename = fields.Char("File Name", size=64)
    excel_file = fields.Binary("Excel File")

    def print_manpower_report(self):
        manpower_obj = self.env["manpower.plan.line"]
        report = self
        filename = "Manpower Planning %s.xlsx" % report.fiscal_year_id.name
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet("manpower plan")
        worksheet.set_column("A:A", 25)
        worksheet.set_column("D:D", 10)
        worksheet.set_column("T:T", 10)
        worksheet.set_column("E:E", 15)
        detail_head = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": 12,
                "font_name": "Times New Roman",
            }
        )
        detail_footer = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "right",
                "valign": "vcenter",
                "font_size": 12,
                "font_name": "Times New Roman",
            }
        )
        details_format = workbook.add_format(
            {"font_size": 12, "valign": "vcenter", "font_name": "Times New Roman"}
        )

        # Preparing Dictionary for report
        manpower_dict = {}
        for plan_line in manpower_obj.search(
            [("plan_id.fiscal_year_id", "=", report.fiscal_year_id.id)]
        ):
            manpower_dict.update({plan_line.id: manpower_dict.get(plan_line.id, {})})
            joining_dict = {}
            line_dict = {
                "title": plan_line.job_id.name or "",
                "actual_emp": plan_line.current_employees or 0,
                "forecasted_leavers": plan_line.leaving_employees,
                "calculated_emp": plan_line.calculated_employees,
                "critical_roles": plan_line.critical_roles,
                "expected_emp": plan_line.expected_employees,
                "future_strength": plan_line.future_strength,
            }

            for joining in plan_line.joining_months:
                joining_dict.update({joining.period_id.name: joining.joining_employees})
            line_dict.update({"joining_months": joining_dict})
            manpower_dict.update({plan_line.id: line_dict})

        worksheet.merge_range(
            0,
            3,
            0,
            7,
            "Manpowerplan Report for :%s" % (report.fiscal_year_id.name),
            detail_head,
        )
        worksheet.write(2, 0, "Title", detail_head)
        worksheet.write(2, 2, "Actual \n Emp", detail_head)
        worksheet.write(2, 3, "Forecasted \n Leavers", detail_head)
        worksheet.write(
            2, 4, "Actual Emp - \n Forecasted Leavers \n E(C-D)", detail_head
        )
        worksheet.write(2, 5, "Critical \n Roles", detail_head)
        worksheet.write(2, 6, "Expected \n New \n Hires", detail_head)
        first_row = 1
        from_col = to_col = 7
        all_col_dict = {
            "title": 0,
            "actual_emp": 2,
            "forecasted_leavers": 3,
            "calculated_emp": 4,
            "critical_roles": 5,
            "expected_emp": 6,
        }
        for period in report.fiscal_year_id.period_ids:
            worksheet.write(3, to_col, period.name, detail_head)
            all_col_dict.update({period.name: to_col})
            to_col += 1
        all_col_dict.update({"future_strength": to_col})
        worksheet.merge_range(2, from_col, 2, to_col - 1, "Expected Month", detail_head)
        worksheet.write(2, to_col, "Future \n Workforce", detail_head)

        worksheet.set_row(2, 45)
        worksheet.freeze_panes(2, 5)
        actual_data_row = 3
        for plan_dict in manpower_dict.values():
            actual_data_row += 1
            for plan_key in plan_dict.keys():
                if plan_key != "joining_months":
                    worksheet.write(
                        actual_data_row,
                        all_col_dict.get(plan_key),
                        plan_dict[plan_key],
                        details_format,
                    )
                else:
                    month_dict = plan_dict[plan_key]
                    for month in plan_dict[plan_key]:
                        worksheet.write(
                            actual_data_row,
                            all_col_dict.get(month),
                            month_dict[month],
                            details_format,
                        )
        worksheet.set_row(actual_data_row + 1, 30, detail_head)
        worksheet.write(
            actual_data_row + 1, all_col_dict.get("title"), "Total", detail_head
        )
        for col in range(2, all_col_dict.get("future_strength") + 1):
            service_first = xl_rowcol_to_cell(first_row + 1, col)
            service_last = xl_rowcol_to_cell(actual_data_row, col)
            worksheet.write_formula(
                actual_data_row + 1,
                col,
                "{=SUM(%s:%s)}" % (service_first, service_last),
                detail_footer,
            )
        workbook.close()
        export_id = self.env["manpower.report"].create(
            {
                "fiscal_year_id": report.fiscal_year_id.id,
                "excel_file": base64.encodebytes(fp.getvalue()),
                "filename": filename,
            }
        )
        fp.close()

        return {
            "name": "Manpower Report",
            "view_mode": "form",
            "res_id": export_id.id,
            "res_model": "manpower.report",
            "type": "ir.actions.act_window",
            "context": self.env.context,
            "target": "new",
        }
