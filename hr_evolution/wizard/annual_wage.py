# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, tools, _
from io import BytesIO
import xlsxwriter
import base64
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class AnnualWageSqlView(models.Model):
    _name = "annual.wage.sql"
    _description = "Annual Wage Sql View"
    _auto = False

    emp_no = fields.Char("Employee Number")
    emp_name = fields.Char("Name")
    service_year = fields.Integer("Service Year")
    belt_id = fields.Many2one("belt.level", string="Belt level")
    department_id = fields.Many2one("hr.department", string="Departments")
    current_wage = fields.Float("Current Wage")

    def init(self):
        """
        Creates a SQL view named `annual_wage_sql` that combines employee data with their
        current wage information.
        """
        tools.drop_view_if_exists(self._cr, "annual_wage_sql")
        self._cr.execute(
            """
            CREATE OR REPLACE VIEW annual_wage_sql AS (
                SELECT row_number() OVER() AS id,
                    e.code AS emp_no,
                    e.name AS emp_name,
                    e.service_year AS service_year,
                    e.belt_level_id AS belt_id,
                    e.department_id AS department_id,
                    c.wage AS current_wage
                -- AS wage_measure
                FROM hr_employee e
                JOIN hr_contract c ON e.contract_id = c.id
            )
            """
        )


class AnnualBelt(models.TransientModel):
    _name = "annual.belt.report"
    _description = "Annual Belt Report"

    belt_id = fields.Many2one("belt.level", string="Belt level")
    no_of_emp = fields.Integer("Employees", compute="calculate_no_of_emp")

    def calculate_no_of_emp(self):
        for rec in self:
            employees = self.env["hr.employee"].search(
                [("belt_level_id", "=", rec.belt_id.id)]
            )
            rec.no_of_emp = len(employees)


class AnnualWage(models.TransientModel):
    _name = "annual.wage.report"
    _description = "Annual Wage Report"

    year_id = fields.Many2one("year.year", string="Year")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    min_wage = fields.Integer(string="Min Wage")
    max_wage = fields.Integer(string="Max Wage")
    class_interval = fields.Integer(string="Class Interval", default="1")

    @api.constrains("min_wage", "max_wage", "class_interval")
    def check_wage_range(self):
        for rec in self:
            if rec.min_wage <= 0 or rec.max_wage <= 0:
                raise UserError(_("Min Wage and Max Wage must be greater than 0."))

            if rec.min_wage and rec.max_wage and rec.min_wage > rec.max_wage:
                raise UserError(_("Max Wage must be greater than Min wage."))

            if rec.class_interval <= 0:
                raise UserError(_("Class Interval must be greater than 0."))

    def get_appraisal(self, employee, year):
        appraisal_ids = self.env["hr.emp.appraisal"].search(
            [("employee_id", "=", employee.id)]
        )
        appraisal_ids = appraisal_ids.filtered(
            lambda l: l.appraisal_end_date.year == year
        )
        end_date = (
            appraisal_ids.mapped("appraisal_end_date")
            and max(appraisal_ids.mapped("appraisal_end_date"))
            or False
        )
        appraisal = appraisal_ids.filtered(lambda l: l.appraisal_end_date == end_date)
        return appraisal and appraisal[0]

    def get_current_year(self):
        current_year = self.year_id.date_start.year
        return current_year

    def get_previous_year(self):
        previous_year_date = self.year_id.date_start - relativedelta(days=1)
        previous_year = previous_year_date.year
        return previous_year

    def get_employee_list(self):
        employees_list = []
        employees = self.env["hr.employee"].search(
            [("company_id", "=", self.company_id.id)]
        )
        previous_year_date = self.year_id.date_start - relativedelta(days=1)
        previous_year = previous_year_date.year
        current_year = self.year_id.date_start.year
        for emp in employees:
            previous_appraisal = self.get_appraisal(emp, previous_year)
            current_appraisal = self.get_appraisal(emp, current_year)
            contract = emp.get_current_contracts()
            hours_per_day = (
                contract and contract.resource_calendar_id.hours_per_day or 0.0
            )
            current_wage = (
                contract
                and contract.wage
                and (contract.wage / 30) / hours_per_day
                or 0.0
            )
            current_wage = "%.2f" % current_wage
            emp_dict = {
                "code": emp.code,
                "name": emp.name,
                "dept": emp.department_id.name,
                "location": emp.branch_id.name,
                "hire_date": emp.date_of_join,
                "previous_completion_date": previous_appraisal
                and previous_appraisal.appraisal_end_date
                or "",
                "current_completion_date": current_appraisal
                and current_appraisal.appraisal_end_date
                or "",
                "previous_belt_level_rating": previous_appraisal
                and previous_appraisal.belt_level_rating
                or "",
                "job_level_rating": current_appraisal
                and current_appraisal.job_level_rating
                or 0.0,
                "belt_level_rating": current_appraisal
                and current_appraisal.belt_level_rating
                or 0.0,
                "current_wage": current_wage or 0.0,
                "current_belt_pay_level": emp.belt_id and emp.belt_id.name or "",
                "next_belt_pay_level": current_appraisal
                and current_appraisal.next_belt_pay_level
                or "",
                "new_wage_level": current_appraisal
                and current_appraisal.plant_manager_new_belt_level
                or 0.0,
                "total_year": emp.service_year,
            }
            employees_list.append(emp_dict)
        return employees_list

    def get_current_wage_level(self):
        wage_level_details = []
        min_range = self.min_wage
        while min_range < self.max_wage:
            max_range = min_range + (self.class_interval - 0.01)
            if max_range > self.max_wage:
                max_range = self.max_wage - 0.01

            no_of_emp = 1
            wage_level_dict = {
                "min_range": min_range,
                "max_range": "%.2f" % (max_range),
                "no_of_emp": no_of_emp,
            }
            wage_level_details.append(wage_level_dict)
            min_range += self.class_interval
        return wage_level_details

    def get_emp_no(self, min_range, max_range):
        no_of_emp = 0
        employees = self.env["hr.employee"].search(
            [("company_id", "=", self.company_id.id)]
        )
        for emp in employees:
            contract = emp.get_current_contracts()
            hours_per_day = (
                contract and contract.resource_calendar_id.hours_per_day or 0.0
            )
            current_wage = (
                contract
                and contract.wage
                and (contract.wage / 30) / hours_per_day
                or 0.0
            )

            if float(min_range) <= current_wage and float(max_range) >= current_wage:
                no_of_emp += 1
        return no_of_emp

    def get_total_belt_level(self):
        belt_level_list = []
        belt_levels = self.env["belt.level"].search([])
        for belt in belt_levels:
            employees = self.env["hr.employee"].search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("belt_level_id", "=", belt.id),
                ]
            )
            belt_level_dict = {
                "belt_level": belt.name,
                "no_of_emp": len(employees) or 0,
            }
            belt_level_list.append(belt_level_dict)
        return belt_level_list

    def get_dept_emp_details(self):
        dept_emp_list = []
        departments = self.env["hr.department"].search([])
        for department in departments:
            employees = self.env["hr.employee"].search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("department_id", "=", department.id),
                ]
            )
            department_dict = {
                "department": department.name,
                "no_of_emp": len(employees) or 0,
            }
            dept_emp_list.append(department_dict)
        return dept_emp_list

    def get_total_year_service_details(self):
        year_emp_list = []
        year_of_service_list = [(0, 1), (2, 4), (5, 9), (10, 14)]
        for year in year_of_service_list:
            employees = self.env["hr.employee"].search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("service_year", ">=", year[0]),
                    ("service_year", "<=", year[1]),
                ]
            )
            year_dict = {
                "min_year": year[0],
                "max_year": year[1],
                "no_of_emp": len(employees) or 0,
            }
            year_emp_list.append(year_dict)
        return year_emp_list

    def print_excel_reports(self):
        filename = "Annual_wage_Report.xlsx"
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet("Annual Wage")
        worksheet.set_row(0, 35)
        worksheet.set_column("A:A", 15)
        worksheet.set_column("B:E", 20)
        worksheet.set_column("F:G", 25)
        worksheet.set_column("H:L", 20)
        worksheet.set_column("M:N", 40)

        heading = workbook.add_format(
            {
                "bold": 1,
                "font_size": 15,
                "align": "center",
                "font_name": "Times New Roman",
                "text_wrap": True,
                "bg_color": "#D3D3D3",
            }
        )
        data = workbook.add_format(
            {
                "align": "center",
                "text_wrap": True,
            }
        )
        row = 0
        col = 0
        previous_year_date = self.year_id.date_start - relativedelta(days=1)
        previous_year = previous_year_date.year
        current_year = self.year_id.date_start.year
        worksheet.write(row, col, "Team #", heading)
        worksheet.write(row, col + 1, "Team Member", heading)
        worksheet.write(row, col + 2, "Dept.", heading)
        worksheet.write(row, col + 3, "Location", heading)
        worksheet.write(row, col + 4, "Hire Date", heading)
        worksheet.write(
            row,
            col + 5,
            "Evaluation Completion Date %s" % previous_year,
            heading,
        )
        worksheet.write(
            row,
            col + 6,
            "Evaluation Completion Date %s" % current_year,
            heading,
        )
        worksheet.write(row, col + 7, "Belt Level Rating %s" % previous_year, heading)
        worksheet.write(row, col + 8, "Job Level Rating %s" % current_year, heading)
        worksheet.write(row, col + 9, "Belt Level Rating %s" % current_year, heading)
        worksheet.write(row, col + 10, "Current Wage", heading)
        worksheet.write(row, col + 11, "Current Belt Pay Level", heading)
        worksheet.write(row, col + 12, "Promote to next Belt Pay Level", heading)
        worksheet.write(
            row,
            col + 13,
            "Plant Manager's Recommended New Wage Level",
            heading,
        )
        worksheet.write(row, col + 14, "Year of Service", heading)
        row += 1
        for emp in self.get_employee_list():
            worksheet.write(row, col, emp.get("code") or "", data)
            worksheet.write(row, col + 1, emp.get("name") or "", data)
            worksheet.write(row, col + 2, emp.get("dept") or "", data)
            worksheet.write(row, col + 3, emp.get("location") or "", data)
            worksheet.write(
                row,
                col + 4,
                emp.get("hire_date") and str(emp.get("hire_date")) or "",
                data,
            )
            worksheet.write(
                row,
                col + 5,
                emp.get("previous_completion_date")
                and str(emp.get("previous_completion_date"))
                or "",
                data,
            )
            worksheet.write(
                row,
                col + 6,
                emp.get("current_completion_date")
                and str(emp.get("current_completion_date"))
                or "",
                data,
            )
            worksheet.write(
                row, col + 7, emp.get("previous_belt_level_rating") or "", data
            )
            worksheet.write(row, col + 8, emp.get("job_level_rating") or "", data)
            worksheet.write(row, col + 9, emp.get("belt_level_rating") or "", data)
            worksheet.write(row, col + 10, emp.get("current_wage") or "", data)
            worksheet.write(
                row, col + 11, emp.get("current_belt_pay_level") or "", data
            )
            worksheet.write(row, col + 12, emp.get("next_belt_pay_level") or "", data)
            worksheet.write(row, col + 13, emp.get("new_wage_level") or "", data)
            worksheet.write(row, col + 14, emp.get("total_year") or "", data)
            row += 1

        row += 2
        data_graph = workbook.add_format(
            {
                "align": "center",
                "text_wrap": True,
                "border": 1,
            }
        )

        worksheet_graph = workbook.add_worksheet("Annual Wage Graph")
        worksheet_graph.set_column("A:M", 15)

        current_wage_level_details = self.get_current_wage_level()
        new_row = 0
        new_col = 0
        if current_wage_level_details:
            worksheet_graph.merge_range(
                new_row,
                0,
                new_row + 1,
                5,
                "Current belt level is based on current wage level",
                heading,
            )
            new_row += 2
            for wage_dict in current_wage_level_details:
                worksheet_graph.write(
                    new_row,
                    new_col,
                    "%s - %s" % (wage_dict.get("min_range"), wage_dict.get("max_range"))
                    or "",
                    data_graph,
                )
                worksheet_graph.write(
                    new_row + 1,
                    new_col,
                    self.get_emp_no(
                        wage_dict.get("min_range"), wage_dict.get("max_range")
                    )
                    or 0,
                    data_graph,
                )
                new_col += 1
            chart_pie = workbook.add_chart({"type": "pie"})
            chart_pie.add_series(
                {
                    "categories": [
                        "Annual Wage Graph",
                        new_row,
                        0,
                        new_row,
                        new_col - 1,
                    ],
                    "values": [
                        "Annual Wage Graph",
                        new_row + 1,
                        0,
                        new_row + 1,
                        new_col - 1,
                    ],
                    "data_labels": {
                        "value": True,
                        "separator": "\n",
                        "position": "center",
                    },
                    "points": [],
                }
            )
            chart_pie.set_title(
                {"name": "Current belt level is based on current wage level"}
            )
            chart_pie.set_size({"x_scale": 1.5, "y_scale": 2})
            worksheet_graph.insert_chart(new_row + 3, 0, chart_pie)

        new_row += 40
        new_col = 0
        total_belt_level_details = self.get_total_belt_level()
        if total_belt_level_details:
            new_row += 2
            for belt_level_dict in total_belt_level_details:
                new_col += 1
                worksheet_graph.write(
                    new_row,
                    new_col,
                    belt_level_dict.get("belt_level") or "",
                    data_graph,
                )
                worksheet_graph.write(
                    new_row + 1,
                    new_col,
                    belt_level_dict.get("no_of_emp") or 0,
                    data_graph,
                )

            worksheet_graph.merge_range(
                new_row - 2, 0, new_row - 1, new_col, "Total Belt", heading
            )

            chart_pie = workbook.add_chart({"type": "pie"})
            chart_pie.add_series(
                {
                    "categories": [
                        "Annual Wage Graph",
                        new_row,
                        1,
                        new_row,
                        new_col,
                    ],
                    "values": [
                        "Annual Wage Graph",
                        new_row + 1,
                        1,
                        new_row + 1,
                        new_col,
                    ],
                    "data_labels": {
                        "value": True,
                        "separator": "\n",
                        "position": "center",
                    },
                    "points": [],
                }
            )
            chart_pie.set_title({"name": "Total Belt"})
            chart_pie.set_size({"x_scale": 1.5, "y_scale": 2})
            worksheet_graph.insert_chart(new_row + 3, 0, chart_pie)

        new_row += 40
        new_col = 0
        dept_emp_details = self.get_dept_emp_details()
        if dept_emp_details:
            new_row += 2
            for dept_dict in dept_emp_details:
                worksheet_graph.write(
                    new_row,
                    new_col,
                    dept_dict.get("department") or "",
                    data_graph,
                )
                worksheet_graph.write(
                    new_row + 1,
                    new_col,
                    dept_dict.get("no_of_emp") or 0,
                    data_graph,
                )
                new_col += 1
            worksheet_graph.merge_range(
                new_row - 2, 0, new_row - 1, new_col, "Departments", heading
            )

            chart_pie = workbook.add_chart({"type": "pie"})
            chart_pie.add_series(
                {
                    "categories": [
                        "Annual Wage Graph",
                        new_row,
                        0,
                        new_row,
                        new_col - 1,
                    ],
                    "values": [
                        "Annual Wage Graph",
                        new_row + 1,
                        0,
                        new_row + 1,
                        new_col - 1,
                    ],
                    "data_labels": {
                        "value": True,
                        "separator": "\n",
                        "position": "center",
                    },
                    "points": [],
                }
            )
            chart_pie.set_title({"name": "Departments"})
            chart_pie.set_size({"x_scale": 1.5, "y_scale": 2})
            worksheet_graph.insert_chart(new_row + 3, 0, chart_pie)

        new_row += 40
        new_col = 0
        total_year_service_details = self.get_total_year_service_details()
        if total_year_service_details:
            new_row += 2
            for year_dict in total_year_service_details:
                worksheet_graph.write(
                    new_row,
                    new_col,
                    "%s - %s" % (year_dict.get("min_year"), year_dict.get("max_year"))
                    or "",
                    data_graph,
                )
                worksheet_graph.write(
                    new_row + 1,
                    new_col,
                    year_dict.get("no_of_emp") or 0,
                    data_graph,
                )
                new_col += 1
            worksheet_graph.merge_range(
                new_row - 2,
                0,
                new_row - 1,
                new_col,
                "Total Years of Service ",
                heading,
            )

            chart_pie = workbook.add_chart({"type": "pie"})
            chart_pie.add_series(
                {
                    "categories": [
                        "Annual Wage Graph",
                        new_row,
                        0,
                        new_row,
                        new_col - 1,
                    ],
                    "values": [
                        "Annual Wage Graph",
                        new_row + 1,
                        0,
                        new_row + 1,
                        new_col - 1,
                    ],
                    "data_labels": {
                        "value": True,
                        "separator": "\n",
                        "position": "center",
                    },
                    "points": [],
                }
            )
            chart_pie.set_title({"name": "Total Years of Service"})
            chart_pie.set_size({"x_scale": 1.5, "y_scale": 2})
            worksheet_graph.insert_chart(new_row + 3, 0, chart_pie)

        workbook.close()
        result = base64.encodebytes(fp.getvalue())
        fp.close()
        excel_file = self.env["ir.attachment"].create(
            {
                "name": filename,
                "datas": result,
                "res_model": "emp.exit.wizard",
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

    def print_pdf_reports(self):
        data = self.read()[0]
        data.update({"company": self.company_id.id})
        return self.env.ref("hr_evolution.action_report_annual_wage").report_action(
            self, data=data
        )
