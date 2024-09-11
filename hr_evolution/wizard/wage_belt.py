# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, tools, _
from io import BytesIO
import xlsxwriter
import base64
from bs4 import BeautifulSoup


class WageBeltView(models.Model):
    _name = "wage.belt.view"
    _description = "Wage Belt View"
    _auto = False

    branch_id = fields.Many2one("hr.branch", string="Location")
    dept_id = fields.Many2one("hr.department", string="Department")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    belt_id = fields.Many2one("belt.level", string="Belt Level")
    probation_hrly_wage = fields.Float(string="Base Hrly Wage Level (Probation)")
    hrly_wage = fields.Float(string="Hrly Wage Level (after 3 months)")
    probation_note = fields.Char(string="Annual evaluations after 3 month probation")

    def init(self):
        """
        Creates a view in the database that combines data from multiple tables
        related to employee information and wages.
        """
        tools.drop_view_if_exists(self._cr, "wage_belt_view")
        self._cr.execute(
            """
            CREATE OR REPLACE VIEW wage_belt_view AS (
                SELECT row_number() OVER() AS id,
                e.branch_id AS branch_id,
                e.belt_level_id AS belt_id,
                e.department_id AS dept_id,
                e.id AS employee_id,
                p.wage_per_hour AS probation_hrly_wage,
                CASE WHEN c.wage IS NOT NULL THEN SUM(c.wage / 30 / 8) ELSE 0.0 END AS hrly_wage,
                p.review AS probation_note
                FROM hr_employee e
                LEFT JOIN hr_contract c ON c.id = e.contract_id
                LEFT JOIN emp_probation_review p ON c.probation_id = p.id OR p.employee_id = e.id AND p.state IN ('approve', 'done')
                -- WHERE e.department_id IN %s
                GROUP BY e.branch_id, e.belt_level_id, e.department_id, e.id, c.wage, p.wage_per_hour, p.review
            )
            """
        )


class WageBeltWizard(models.TransientModel):
    _name = "wage.belt.wizard"
    _description = "Wage Belt Wizard"

    company_ids = fields.Many2many("res.company", string="Company", required=True)
    department_ids = fields.Many2many("hr.department", string="Departments")

    @api.model
    def default_get(self, default_fields):
        """
        set default value
        """
        res = super(WageBeltWizard, self).default_get(default_fields)
        context = dict(self.env.context) or {}
        company_ids = context.get("allowed_company_ids") or []
        departments = self.env["hr.department"].search(
            [("company_id", "in", company_ids)]
        )
        department_ids = departments.ids or []
        res["company_ids"] = [(6, 0, company_ids)]
        res["department_ids"] = [(6, 0, department_ids)]
        return res

    @api.onchange("company_ids")
    def get_department(self):
        if self.company_ids:
            dept_ids = self.env["hr.department"].search(
                [("company_id", "in", self.company_ids.ids)]
            )
            self.department_ids = [(6, 0, dept_ids.ids)]

    def get_probation_wage(self, employee):
        contract = employee.get_current_contracts()
        if contract and contract.probation_id:
            return (
                contract.probation_id.wage_per_hour,
                contract.probation_id.review,
            )

        probation_id = self.env["emp.probation.review"].search(
            [
                ("employee_id", "=", employee.id),
                ("state", "in", ["approve", "done"]),
            ],
            limit=1,
        )
        if probation_id:
            return probation_id.wage_per_hour, probation_id.review

        return 0.0, None

    def get_current_wage(self, employee):
        contract = employee.get_current_contracts()
        if contract and contract.wage:
            hours_per_day = (
                contract.resource_calendar_id
                and contract.resource_calendar_id.hours_per_day
                or 8
            )
            wage_per_hour = (contract.wage / 30) / hours_per_day
            return wage_per_hour
        return 0.0

    def get_dept(self, company):
        data = []
        departments = self.department_ids.filtered(lambda l: l.company_id == company)
        for department in departments:
            data.append(department.name)
        return departments

    def get_emp(self, department):
        data = []
        employee_ids = self.env["hr.employee"].search(
            [("department_id", "=", department.id)]
        )
        return employee_ids

    def print_pdf(self):
        data = self.read()[0]
        return self.env.ref("hr_evolution.action_report_wage_belt").report_action(
            self, data=data
        )

    def print_excel(self):
        filename = "Wagebelt.xlsx"
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet("Company BlackBelt Grid ")
        worksheet.set_row(0, 35)
        worksheet.set_column("A:G", 27)

        heading = workbook.add_format(
            {
                "bold": 1,
                "font_size": 15,
                "align": "center",
                "font_name": "Times New Roman",
                "text_wrap": True,
            }
        )

        row = 0
        col = 0

        worksheet.write(row, col, "Location", heading)
        worksheet.write(row, col + 1, "Department", heading)
        worksheet.write(row, col + 2, "Employee", heading)
        worksheet.write(row, col + 3, "Belt Level", heading)
        worksheet.write(row, col + 4, "Base Hrly Wage Level (Probation)", heading)
        worksheet.write(row, col + 5, "Hrly Wage Level (after 3 months)", heading)
        worksheet.write(
            row, col + 6, "Annual evaluations after 3 month probation", heading
        )
        row += 1

        for company in self.company_ids:
            worksheet.write(row, col, company.name)
            department_ids = self.department_ids.filtered(
                lambda l: l.company_id == company
            )
            for department in department_ids:
                worksheet.write(row, col + 1, department.name)
                employee_ids = self.env["hr.employee"].search(
                    [("department_id", "=", department.id)]
                )
                for employee in employee_ids:
                    worksheet.write(row, col + 2, employee.name)
                    worksheet.write(row, col + 3, employee.belt_id.name or "")
                    probation_wage, probation_note = self.get_probation_wage(employee)
                    current_wage = self.get_current_wage(employee)
                    worksheet.write(row, col + 4, "%.2f" % (probation_wage or 0.0))
                    worksheet.write(row, col + 5, "%.2f" % (current_wage or 0.0))
                    if probation_note:
                        soup = BeautifulSoup(probation_note)
                        worksheet.write(row, col + 6, (soup.get_text() or ""))
                    row += 1
                row += 1
            row += 2

        workbook.close()
        result = base64.encodebytes(fp.getvalue())
        fp.close()
        excel_file = self.env["ir.attachment"].create(
            {
                "name": filename,
                "datas": result,
                "res_model": "first.signin",
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
