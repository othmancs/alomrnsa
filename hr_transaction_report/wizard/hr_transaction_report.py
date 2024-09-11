# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import base64
from datetime import datetime
from io import BytesIO

import xlsxwriter
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT
from odoo.tools.misc import format_date as odoo_format_date


class HrTransactionReport(models.TransientModel):
    _name = "hr.transaction.report"
    _description = "HR Transaction Report"

    @api.model
    def default_get(self, default_fields):
        """
        Override method for update default values
        """
        res = super(HrTransactionReport, self).default_get(default_fields)
        res.update(
            {
                "name": "Transaction Report %s" % fields.Date.today().strftime("%B %Y"),
                "start_date": fields.Date.today() + relativedelta(day=1),
                "end_date": fields.Date.today()
                + relativedelta(day=1, months=+1, days=-1),
            }
        )
        return res

    name = fields.Char(string="Report Name")
    start_date = fields.Date(
        string="Start Date", default=fields.Date.today(), required=True
    )
    end_date = fields.Date(
        string="End Date", default=fields.Date.today(), required=True
    )
    employee_selection = fields.Selection(
        [("all", "All"), ("selected", "Selected")],
        string="Employee Selection",
        required=True,
        default="all",
    )
    employee_ids = fields.Many2many("hr.employee", string="Employees")
    filename = fields.Char(string="File Name", size=64)
    excel_file = fields.Binary(string="Excel File")

    add_vacation = fields.Boolean(string="Vacation Summary", default=True)
    add_transfer = fields.Boolean(string="Transfer Summary", default=True)
    add_clearance = fields.Boolean(string="Clearance Summary", default=True)
    add_other_allowance = fields.Boolean(string="Other Allowance Summary", default=True)
    add_new_staff = fields.Boolean(string="New Staff Summary", default=True)
    add_sick_leave = fields.Boolean(string="Leaves Summary", default=True)
    add_loan = fields.Boolean(string="Loan Summary", default=True)
    add_warning = fields.Boolean(string="Warning Summary", default=True)
    add_cost_report = fields.Boolean(string="Cost Summary", default=True)
    payslip_export_id = fields.Many2one("hr.payslip.export", "Export Structure")

    _sql_constraints = [
        ("date_check", "CHECK((start_date <= end_date))", "Please enter valid date")
    ]

    def get_employee_vacation_details(self, employees, vacation_details):
        date_from = datetime.strptime(self.start_date.strftime(DT), DT)
        date_to = datetime.strptime(self.end_date.strftime(DT), DT)
        vacation_ids = self.env["hr.vacation"].search(
            [
                ("employee_id", "in", employees.ids),
                ("date_start", ">=", date_from),
                ("date_to", "<=", date_to),
                ("state", "not in", ("draft", "cancel")),
            ],
            order="date_start, state, employee_id",
        )
        for vacation in vacation_ids:
            vacation_details.append(
                {
                    "employee_code": vacation.employee_id.code,
                    "employee_name": vacation.employee_id.name,
                    "department": vacation.employee_id.department_id.name
                    if vacation.employee_id.department_id
                    else "",
                    "vacation_type": "unpaid",
                    "from_date": vacation.date_start,
                    "to_date": vacation.date_to,
                    "return_date": vacation.return_to_work_date
                    if vacation.return_to_work_date
                    else "",
                }
            )

    def get_employee_transfer_details(self, employees, transfer_details):
        transfer_employee_ids = self.env["transfer.employee"].search(
            [
                ("employee_id", "in", employees.ids),
                ("effective_date", ">=", self.start_date),
                ("effective_date", "<=", self.end_date),
                ("state", "=", "done"),
            ],
            order="effective_date, state, employee_id",
        )
        for transfer in transfer_employee_ids:
            transfer_details.append(
                {
                    "employee_code": transfer.employee_id.code,
                    "employee_name": transfer.employee_id.name,
                    "old_branch": transfer.branch_id.name if transfer.branch_id else "",
                    "new_branch": transfer.new_branch_id.name
                    if transfer.new_branch_id
                    else "",
                    "transfer_date": transfer.effective_date
                    if transfer.effective_date
                    else "",
                }
            )

    def get_employee_clearance_details(self, employees, clearance_details):
        date_from = datetime.strptime(self.start_date.strftime(DT), DT)
        date_to = datetime.strptime(self.end_date.strftime(DT), DT)
        clearance_employee_ids = self.env["hr.employee.clearance"].search(
            [
                ("employee_id", "in", employees.ids),
                ("approved_date", ">=", date_from),
                ("approved_date", "<=", date_to),
                ("state", "not in", ["draft", "refuse"]),
            ],
            order="approved_date, state, employee_id, department_id",
        )
        for clearance in clearance_employee_ids:
            clearance_details.append(
                {
                    "employee_code": clearance.employee_id.code,
                    "employee_name": clearance.employee_id.name,
                    "department": clearance.department_id.name
                    if clearance.department_id
                    else "",
                    "reason": "",
                    "last_day": clearance.last_working_day
                    if clearance.last_working_day
                    else "",
                }
            )

    def get_employee_other_hr_payslip_details(
        self, employees, other_hr_payslip_details
    ):
        other_hr_payslip_ids = self.env["other.hr.payslip"].search(
            [
                ("employee_id", "in", employees.ids),
                ("date", ">=", self.start_date),
                ("date", "<=", self.end_date),
                ("state", "=", "done"),
            ],
            order="date, department_id, employee_id",
        )
        for other_hr_payslip in other_hr_payslip_ids:
            other_hr_payslip_details.append(
                {
                    "employee_code": other_hr_payslip.employee_id.code,
                    "employee_name": other_hr_payslip.employee_id.name,
                    "department": other_hr_payslip.department_id.name
                    if other_hr_payslip.department_id
                    else "",
                    "operation_type": dict(
                        other_hr_payslip._fields["operation_type"].selection
                    ).get(other_hr_payslip.operation_type),
                    "description": other_hr_payslip.description,
                }
            )

    def get_new_joining_emp_details(self, new_joining_emp_details):
        employees_ids = self.env["hr.employee"].search(
            [
                ("date_of_join", ">=", self.start_date),
                ("date_of_join", "<=", self.end_date),
            ],
            order="date_of_join, department_id",
        )
        for emp in employees_ids:
            new_joining_emp_details.append(
                {
                    "employee_code": emp.code,
                    "employee_name": emp.name,
                    "job_title": emp.job_title or "",
                    "department": emp.department_id.name if emp.department_id else "",
                    "hiring_date": emp.date_of_join if emp.date_of_join else "",
                }
            )

    def get_employee_leaves_details(self, employees, leaves_details):
        date_from = datetime.strptime(self.start_date.strftime(DT), DT)
        date_to = datetime.strptime(self.end_date.strftime(DT), DT)
        leave_ids = self.env["hr.leave"].search(
            [
                ("employee_id", "in", employees.ids),
                ("date_from", ">=", date_from),
                ("date_to", "<=", date_to),
                ("state", "=", "validate"),
            ],
            order="date_from, employee_id, department_id",
        )
        for leave in leave_ids:
            leaves_details.append(
                {
                    "employee_code": leave.employee_id.code,
                    "employee_name": leave.employee_id.name,
                    "department": leave.employee_id.department_id.name
                    if leave.employee_id.department_id
                    else "",
                    "leave_type": leave.holiday_status_id.name,
                    "from_date": leave.date_from,
                    "to_date": leave.date_to,
                }
            )

    def get_employee_loan_details(self, employees, loan_details):
        loan_ids = self.env["hr.loan"].search(
            [("employee_id", "in", employees.ids)],
            order="state, employee_id, department_id",
        )
        for loan in loan_ids:
            deduction = 0.0
            installment_lines = loan.installment_lines.filtered(
                lambda i: i.date >= self.start_date and i.date <= self.end_date
            )
            if installment_lines:
                for line in installment_lines:
                    deduction += line.amount
            loan_details.append(
                {
                    "employee_code": loan.employee_id.code,
                    "employee_name": loan.employee_id.name,
                    "branch": loan.branch_id.name,
                    "location": loan.employee_id.work_location_id.name,
                    "date": loan.request_date,
                    "loan_amount": loan.loan_amount,
                    "monthly_payment": loan.loan_amount / loan.duration
                    if loan.duration != 0
                    else 0.0,
                    "total_deduction": loan.amount_paid,
                    "deduction": deduction,
                    "balance": loan.amount_to_pay,
                    "status": dict(loan._fields["state"].selection).get(loan.state),
                }
            )

    def get_employee_warning_details(self, employees, warning_details):
        date_from = datetime.strptime(self.start_date.strftime(DT), DT)
        date_to = datetime.strptime(self.end_date.strftime(DT), DT)
        warning_ids = self.env["issue.warning"].search(
            [
                ("warning_date", ">=", date_from),
                ("warning_date", "<=", date_to),
                ("state", "=", "done"),
            ],
            order="warning_date",
        )
        for warning in warning_ids:
            employee_ids = warning.employee_ids
            if warning.target_group == "employee":
                employee_ids = warning.employee_id
            warning_types = []
            for warning_type in warning.warning_types:
                warning_types.append(warning_type.name)
            for emp in employee_ids:
                warning_details.append(
                    {
                        "employee_code": emp.code,
                        "employee_name": emp.name,
                        "warning_action": dict(
                            warning._fields["warning_action"].selection
                        ).get(warning.warning_action),
                        "warning_date": warning.warning_date,
                        "warning_type": ", ".join(warning_types),
                        "description": warning.description,
                    }
                )

    def get_employee_expense_details(self, employees, expense_details, total_expense):
        date_from = datetime.strptime(self.start_date.strftime(DT), DT)
        date_to = datetime.strptime(self.end_date.strftime(DT), DT)
        expense_ids = self.env["hr.expense"].search(
            [
                ("employee_id", "in", employees.ids),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
                ("state", "=", "done"),
            ],
            order="date, employee_id",
        )
        for expense in expense_ids:
            expense_details.append(
                {
                    "employee_code": expense.employee_id.code,
                    "employee_name": expense.employee_id.name,
                    "expense_amount": expense.unit_amount,
                    "date": expense.date,
                    "reason": expense.product_id.name,
                    "description": expense.name,
                    "reference": expense.reference,
                }
            )
        for employee in employees:
            expense_amount = sum(
                expense_ids.filtered(lambda e: e.employee_id.id == employee.id).mapped(
                    "unit_amount"
                )
            )
            total_expense.append({employee.id: expense_amount})

    def get_employee_payslip_details(
        self, employees, payslip_details, payslip_headers, total_expense, cost_details
    ):
        date_from = datetime.strptime(self.start_date.strftime(DT), DT)
        date_to = datetime.strptime(self.end_date.strftime(DT), DT)
        payslip_ids = self.env["hr.payslip"].search(
            [
                ("employee_id", "in", employees.ids),
                ("date_from", ">=", date_from),
                ("date_to", "<=", date_to),
                ("state", "=", "done"),
            ],
            order="date_from, employee_id",
        )
        payslip_headers += ["Employee Code", "Employee Name", "Department"]
        rule_codes = []
        rule_ids = self.payslip_export_id.line_ids
        for rule in rule_ids:
            rule_codes.append(rule.rule_id)
            payslip_headers.append(rule.rule_id.code)
        for payslip in payslip_ids:
            payslip_vals = {
                "Employee Code": payslip.employee_id.code,
                "Employee Name": payslip.employee_id.name,
                "Department": payslip.employee_id.department_id.name
                if payslip.employee_id.department_id
                else "",
            }
            for rule in rule_codes:
                payslip_line = payslip.line_ids.filtered(
                    lambda x: x.salary_rule_id.id == rule.id
                )
                if payslip_line:
                    # if payslip_line.code == 'NET':
                    payslip_vals.update({rule.code: payslip_line[0].total})
                else:
                    payslip_vals.update({rule.code: ""})
            payslip_details.append(payslip_vals)
        for employee in employees:
            employee_payslips = payslip_ids.filtered(
                lambda e: e.employee_id.id == employee.id
            )
            net_salary = 0.0
            for emp_payslip in employee_payslips:
                payslip_line = emp_payslip.line_ids.filtered(
                    lambda x: x.code == "NET" and x.salary_rule_id in rule_codes
                )
                if payslip_line:
                    net_salary += payslip_line[0].total
            expense_amount = 0.0
            for expense in total_expense:
                if expense.get(employee.id):
                    expense_amount = expense[employee.id]
            cost_details.append(
                {
                    "employee_code": employee.code,
                    "employee_name": employee.name,
                    "expense_amount": expense_amount,
                    "net_salary": net_salary,
                    "total_cost": expense_amount + net_salary,
                }
            )

    def generate_hr_transaction_excel_report(self):
        self.ensure_one()
        employee_ids = self.employee_ids
        if self.employee_selection == "all":
            employee_ids = self.env["hr.employee"].search([])
        if not employee_ids:
            raise ValidationError(_("Please select employee for print report"))
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        heading_format = workbook.add_format(
            {
                "align": "center",
                "border": 1,
                "bold": True,
                "size": 25,
                "bg_color": "#D3D3D3",
            }
        )
        sub_heading_format = workbook.add_format(
            {
                "align": "center",
                "border": 1,
                "bold": True,
                "size": 18,
                "bg_color": "#D3D3D3",
            }
        )
        cell_heading_format = workbook.add_format(
            {
                "align": "center",
                "bold": True,
                "border": 1,
                "size": 12,
                "bg_color": "#D3D3D3",
            }
        )
        cell_data_format = workbook.add_format(
            {"align": "left", "border": 1, "size": 10}
        )
        cell_amount_format = workbook.add_format(
            {"align": "right", "border": 1, "size": 10}
        )
        heading_data_format = workbook.add_format(
            {"align": "center", "border": 1, "size": 12, "num_format": "#,##0.00"}
        )
        date_time_format = workbook.add_format(
            {"align": "left", "num_format": "mm/dd/yy", "border": 1, "size": 10}
        )
        (
            leaves_details,
            transfer_details,
            clearance_details,
            other_hr_payslip_details,
            new_joining_emp_details,
            loan_details,
            vacation_details,
            warning_details,
            expense_details,
            payslip_details,
            payslip_headers,
            total_expense,
            cost_details,
        ) = ([], [], [], [], [], [], [], [], [], [], [], [], [])

        if (
            not self.add_vacation
            and not self.add_transfer
            and not self.add_clearance
            and not self.add_other_allowance
            and not self.add_new_staff
            and not self.add_sick_leave
            and not self.add_loan
            and not self.add_warning
            and not self.add_cost_report
        ):
            raise ValidationError(
                _("Please select at least one checkbox for print report.")
            )

        if self.add_vacation:
            self.get_employee_vacation_details(employee_ids, vacation_details)
        if self.add_transfer:
            self.get_employee_transfer_details(employee_ids, transfer_details)
        if self.add_clearance:
            self.get_employee_clearance_details(employee_ids, clearance_details)
        if self.add_other_allowance:
            self.get_employee_other_hr_payslip_details(
                employee_ids, other_hr_payslip_details
            )
        if self.add_new_staff:
            self.get_new_joining_emp_details(new_joining_emp_details)
        if self.add_sick_leave:
            self.get_employee_leaves_details(employee_ids, leaves_details)
        if self.add_loan:
            self.get_employee_loan_details(employee_ids, loan_details)
        if self.add_warning:
            self.get_employee_warning_details(employee_ids, warning_details)
        if self.add_cost_report:
            self.get_employee_expense_details(
                employee_ids, expense_details, total_expense
            )
            self.get_employee_payslip_details(
                employee_ids,
                payslip_details,
                payslip_headers,
                total_expense,
                cost_details,
            )

        worksheet_name = "Employees Transaction"
        row, column = 1, 0
        try:
            worksheet = workbook.add_worksheet(worksheet_name)

            worksheet.merge_range("A%s:H%s" % (row, row + 2), self.name, heading_format)
            row += 3
            worksheet.set_column("A:A", 5)
            worksheet.set_column("B:B", 20)
            worksheet.set_column("C:C", 20)
            worksheet.set_column("D:D", 20)
            worksheet.set_column("E:E", 20)
            worksheet.set_column("F:F", 20)
            worksheet.set_column("G:G", 20)
            worksheet.set_column("H:H", 20)
            worksheet.set_column("I:I", 20)
            worksheet.set_column("J:J", 20)
            worksheet.set_column("K:K", 20)
            worksheet.set_column("L:L", 20)

            # Report Details
            worksheet.write(row, column + 1, "Start Date", cell_heading_format)
            worksheet.write(row, column + 4, "End Date", cell_heading_format)
            worksheet.write(row + 1, column + 1, "Print Date", cell_heading_format)
            worksheet.write(row + 1, column + 4, "Printed By", cell_heading_format)

            worksheet.write(
                row,
                column + 2,
                odoo_format_date(self.env, self.start_date),
                heading_data_format,
            )
            worksheet.write(
                row,
                column + 5,
                odoo_format_date(self.env, self.end_date),
                heading_data_format,
            )
            worksheet.write(
                row + 1,
                column + 2,
                odoo_format_date(self.env, fields.Date.today()),
                heading_data_format,
            )
            worksheet.write(
                row + 1, column + 5, self.env.user.name, heading_data_format
            )
            row += 3

            if self.add_vacation:
                # Vacation summary details
                worksheet.merge_range(
                    "A%s:H%s" % (row + 2, row + 3),
                    "Vacation Summary",
                    sub_heading_format,
                )
                row += 3
                worksheet.write(row, column, "SN", cell_heading_format)
                worksheet.write(row, column + 1, "Employee Code", cell_heading_format)
                worksheet.write(row, column + 2, "Employee Name", cell_heading_format)
                worksheet.write(row, column + 3, "Department", cell_heading_format)
                worksheet.write(row, column + 4, "Vacation Type", cell_heading_format)
                worksheet.write(row, column + 5, "From", cell_heading_format)
                worksheet.write(row, column + 6, "To", cell_heading_format)
                worksheet.write(row, column + 7, "Return Date", cell_heading_format)
                row += 1
                for num, vacation in enumerate(vacation_details, 1):
                    worksheet.write(row, column, str(num), cell_data_format)
                    worksheet.write(
                        row, column + 1, vacation["employee_code"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 2, vacation["employee_name"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 3, vacation["department"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 4, vacation["vacation_type"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 5, vacation["from_date"], date_time_format
                    )
                    worksheet.write(
                        row, column + 6, vacation["to_date"], date_time_format
                    )
                    worksheet.write(
                        row, column + 7, vacation["return_date"], date_time_format
                    )
                    row += 1

            if self.add_transfer:
                row += 1
                # Transfer details
                worksheet.merge_range(
                    "A%s:F%s" % (row + 2, row + 3), "Transfer", sub_heading_format
                )
                row += 3
                worksheet.write(row, column, "SN", cell_heading_format)
                worksheet.write(row, column + 1, "Employee Code", cell_heading_format)
                worksheet.write(row, column + 2, "Employee Name", cell_heading_format)
                worksheet.write(row, column + 3, "Old Branch", cell_heading_format)
                worksheet.write(row, column + 4, "New Branch", cell_heading_format)
                worksheet.write(row, column + 5, "Transfer Date", cell_heading_format)
                row += 1
                for num_transfer, transfer in enumerate(transfer_details, 1):
                    worksheet.write(row, column, str(num_transfer), cell_data_format)
                    worksheet.write(
                        row, column + 1, transfer["employee_code"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 2, transfer["employee_name"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 3, transfer["old_branch"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 4, transfer["new_branch"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 5, transfer["transfer_date"], date_time_format
                    )
                    row += 1

            if self.add_clearance:
                row += 1
                # Clearance details
                worksheet.merge_range(
                    "A%s:F%s" % (row + 2, row + 3), "Clearance", sub_heading_format
                )
                row += 3
                worksheet.write(row, column, "SN", cell_heading_format)
                worksheet.write(row, column + 1, "Employee Code", cell_heading_format)
                worksheet.write(row, column + 2, "Employee Name", cell_heading_format)
                worksheet.write(row, column + 3, "Department", cell_heading_format)
                worksheet.write(row, column + 4, "Reason", cell_heading_format)
                worksheet.write(row, column + 5, "Last Date", cell_heading_format)
                row += 1
                for num_clearance, clearance in enumerate(clearance_details, 1):
                    worksheet.write(row, column, str(num_clearance), cell_data_format)
                    worksheet.write(
                        row, column + 1, clearance["employee_code"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 2, clearance["employee_name"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 3, clearance["department"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 4, clearance["reason"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 5, clearance["last_day"], date_time_format
                    )
                    row += 1

            if self.add_other_allowance:
                row += 1
                # Other Allowances/Deduction
                worksheet.merge_range(
                    "A%s:F%s" % (row + 2, row + 3),
                    "Other Allowances/Deduction",
                    sub_heading_format,
                )
                row += 3
                worksheet.write(row, column, "SN", cell_heading_format)
                worksheet.write(row, column + 1, "Employee Code", cell_heading_format)
                worksheet.write(row, column + 2, "Employee Name", cell_heading_format)
                worksheet.write(row, column + 3, "Department", cell_heading_format)
                worksheet.write(
                    row, column + 4, "Deduct /Allowances", cell_heading_format
                )
                worksheet.write(row, column + 5, "Reason", cell_heading_format)
                row += 1
                for num_other, other_hr_payslip in enumerate(
                    other_hr_payslip_details, 1
                ):
                    worksheet.write(row, column, str(num_other), cell_data_format)
                    worksheet.write(
                        row,
                        column + 1,
                        other_hr_payslip["employee_code"],
                        cell_data_format,
                    )
                    worksheet.write(
                        row,
                        column + 2,
                        other_hr_payslip["employee_name"],
                        cell_data_format,
                    )
                    worksheet.write(
                        row,
                        column + 3,
                        other_hr_payslip["department"],
                        cell_data_format,
                    )
                    worksheet.write(
                        row,
                        column + 4,
                        other_hr_payslip["operation_type"],
                        cell_data_format,
                    )
                    worksheet.write(
                        row,
                        column + 5,
                        other_hr_payslip["description"],
                        cell_data_format,
                    )
                    row += 1

            if self.add_new_staff:
                row += 1
                # New Staff
                worksheet.merge_range(
                    "A%s:G%s" % (row + 2, row + 3), "New Staff", sub_heading_format
                )
                row += 3
                worksheet.write(row, column, "SN", cell_heading_format)
                worksheet.write(row, column + 1, "Employee Code", cell_heading_format)
                worksheet.write(row, column + 2, "Employee Name", cell_heading_format)
                worksheet.write(row, column + 3, "Job Title", cell_heading_format)
                worksheet.write(row, column + 4, "Department", cell_heading_format)
                worksheet.write(row, column + 5, "Hiring Date", cell_heading_format)
                worksheet.write(row, column + 6, "Notes", cell_heading_format)
                row += 1
                for emp_num, emp in enumerate(new_joining_emp_details, 1):
                    worksheet.write(row, column, str(emp_num), cell_data_format)
                    worksheet.write(
                        row, column + 1, emp["employee_code"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 2, emp["employee_name"], cell_data_format
                    )
                    worksheet.write(row, column + 3, emp["job_title"], cell_data_format)
                    worksheet.write(
                        row, column + 4, emp["department"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 5, emp["hiring_date"], date_time_format
                    )
                    worksheet.write(row, column + 6, "", cell_data_format)
                    row += 1

            if self.add_sick_leave:
                row += 1
                # Leaves summary details
                worksheet.merge_range(
                    "A%s:H%s" % (row + 2, row + 3), "Leave Summary", sub_heading_format
                )
                row += 3
                worksheet.write(row, column, "SN", cell_heading_format)
                worksheet.write(row, column + 1, "Employee Code", cell_heading_format)
                worksheet.write(row, column + 2, "Employee Name", cell_heading_format)
                worksheet.write(row, column + 3, "Department", cell_heading_format)
                worksheet.write(row, column + 4, "Leave Type", cell_heading_format)
                worksheet.write(row, column + 5, "From", cell_heading_format)
                worksheet.write(row, column + 6, "To", cell_heading_format)
                worksheet.write(row, column + 7, "Notes", cell_heading_format)
                row += 1
                for num, leave in enumerate(leaves_details, 1):
                    worksheet.write(row, column, str(num), cell_data_format)
                    worksheet.write(
                        row, column + 1, leave["employee_code"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 2, leave["employee_name"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 3, leave["department"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 4, leave["leave_type"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 5, leave["from_date"], date_time_format
                    )
                    worksheet.write(row, column + 6, leave["to_date"], date_time_format)
                    worksheet.write(row, column + 7, "", cell_data_format)
                    row += 1

            if self.add_loan:
                row += 1
                # Loan details
                worksheet.merge_range(
                    "A%s:L%s" % (row + 2, row + 3), "Loan Summary", sub_heading_format
                )
                row += 3
                worksheet.write(row, column, "SN", cell_heading_format)
                worksheet.write(row, column + 1, "Employee Code", cell_heading_format)
                worksheet.write(row, column + 2, "Employee Name", cell_heading_format)
                worksheet.write(row, column + 3, "Branch", cell_heading_format)
                worksheet.write(row, column + 4, "Location", cell_heading_format)
                worksheet.write(row, column + 5, "Request Date", cell_heading_format)
                worksheet.write(row, column + 6, "Loan Amount", cell_heading_format)
                worksheet.write(row, column + 7, "Monthly Payment", cell_heading_format)
                worksheet.write(row, column + 8, "Total Deduction", cell_heading_format)
                worksheet.write(row, column + 9, "Deduction", cell_heading_format)
                worksheet.write(row, column + 10, "Balance", cell_heading_format)
                worksheet.write(row, column + 11, "Status", cell_heading_format)
                row += 1
                for loan_num, loan in enumerate(loan_details, 1):
                    worksheet.write(row, column, str(loan_num), cell_data_format)
                    worksheet.write(
                        row, column + 1, loan["employee_code"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 2, loan["employee_name"], cell_data_format
                    )
                    worksheet.write(row, column + 3, loan["branch"], cell_data_format)
                    worksheet.write(row, column + 4, loan["location"], cell_data_format)
                    worksheet.write(row, column + 5, loan["date"], date_time_format)
                    worksheet.write(
                        row,
                        column + 6,
                        "{:.2f}".format(loan["loan_amount"]),
                        cell_amount_format,
                    )
                    worksheet.write(
                        row,
                        column + 7,
                        "{:.2f}".format(loan["monthly_payment"]),
                        cell_amount_format,
                    )
                    worksheet.write(
                        row,
                        column + 8,
                        "{:.2f}".format(loan["total_deduction"]),
                        cell_amount_format,
                    )
                    worksheet.write(
                        row,
                        column + 9,
                        "{:.2f}".format(loan["deduction"]),
                        cell_amount_format,
                    )
                    worksheet.write(
                        row,
                        column + 10,
                        "{:.2f}".format(loan["balance"]),
                        cell_amount_format,
                    )
                    worksheet.write(row, column + 11, loan["status"], cell_data_format)
                    row += 1

            if self.add_warning:
                row += 1
                # Warning details
                worksheet.merge_range(
                    "A%s:G%s" % (row + 2, row + 3), "Warning", sub_heading_format
                )
                row += 3
                worksheet.write(row, column, "SN", cell_heading_format)
                worksheet.write(row, column + 1, "Employee Code", cell_heading_format)
                worksheet.write(row, column + 2, "Employee Name", cell_heading_format)
                worksheet.write(row, column + 3, "Warning Action", cell_heading_format)
                worksheet.write(row, column + 4, "Warning Date", cell_heading_format)
                worksheet.write(row, column + 5, "Warning Type", cell_heading_format)
                worksheet.write(row, column + 6, "Notes", cell_heading_format)
                row += 1
                for warning_num, warning in enumerate(warning_details, 1):
                    worksheet.write(row, column, str(warning_num), cell_data_format)
                    worksheet.write(
                        row, column + 1, warning["employee_code"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 2, warning["employee_name"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 3, warning["warning_action"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 4, warning["warning_date"], date_time_format
                    )
                    worksheet.write(
                        row, column + 5, warning["warning_type"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 6, warning["description"], cell_data_format
                    )
                    row += 1

            if self.add_cost_report:
                row += 1
                # Expense details
                worksheet.merge_range(
                    "A%s:H%s" % (row + 2, row + 3), "Expense Report", sub_heading_format
                )
                row += 3
                worksheet.write(row, column, "SN", cell_heading_format)
                worksheet.write(row, column + 1, "Employee Code", cell_heading_format)
                worksheet.write(row, column + 2, "Employee Name", cell_heading_format)
                worksheet.write(row, column + 3, "Expense Amount", cell_heading_format)
                worksheet.write(row, column + 4, "Date", cell_heading_format)
                worksheet.write(row, column + 5, "Reason", cell_heading_format)
                worksheet.write(row, column + 6, "Description", cell_heading_format)
                worksheet.write(row, column + 7, "Reference", cell_heading_format)
                row += 1
                for expense_num, expense in enumerate(expense_details, 1):
                    worksheet.write(row, column, str(expense_num), cell_data_format)
                    worksheet.write(
                        row, column + 1, expense["employee_code"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 2, expense["employee_name"], cell_data_format
                    )
                    worksheet.write(
                        row,
                        column + 3,
                        "{:.2f}".format(expense["expense_amount"]),
                        cell_amount_format,
                    )
                    worksheet.write(row, column + 4, expense["date"], date_time_format)
                    worksheet.write(
                        row, column + 5, expense["reason"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 6, expense["description"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 7, expense["reference"], cell_data_format
                    )
                    row += 1

                row += 1
                # Payslip details
                worksheet.merge_range(
                    "A%s:D%s" % (row + 2, row + 3),
                    "Payslip Details",
                    sub_heading_format,
                )
                row += 3
                worksheet.write(row, column, "SN", cell_heading_format)
                col = column + 1
                for header in payslip_headers:
                    worksheet.write(row, col, header, cell_heading_format)
                    col += 1
                row += 1
                for payslip_num, payslip in enumerate(payslip_details, 1):
                    worksheet.write(row, column, str(payslip_num), cell_data_format)
                    col = column + 1
                    for header in payslip_headers:
                        worksheet.write(row, col, payslip.get(header), cell_data_format)
                        col += 1
                    row += 1

                row += 1
                # Cost details
                worksheet.merge_range(
                    "A%s:F%s" % (row + 2, row + 3), "Cost Report", sub_heading_format
                )
                row += 3
                worksheet.write(row, column, "SN", cell_heading_format)
                worksheet.write(row, column + 1, "Employee Code", cell_heading_format)
                worksheet.write(row, column + 2, "Employee Name", cell_heading_format)
                worksheet.write(row, column + 3, "Expense Amount", cell_heading_format)
                worksheet.write(row, column + 4, "Net Salary", cell_heading_format)
                worksheet.write(row, column + 5, "Total Cost", cell_heading_format)
                row += 1
                for num_cost, cost in enumerate(cost_details, 1):
                    worksheet.write(row, column, str(num_cost), cell_data_format)
                    worksheet.write(
                        row, column + 1, cost["employee_code"], cell_data_format
                    )
                    worksheet.write(
                        row, column + 2, cost["employee_name"], cell_data_format
                    )
                    worksheet.write(
                        row,
                        column + 3,
                        "{:.2f}".format(cost["expense_amount"]),
                        cell_amount_format,
                    )
                    worksheet.write(
                        row,
                        column + 4,
                        "{:.2f}".format(cost["net_salary"]),
                        cell_amount_format,
                    )
                    worksheet.write(
                        row,
                        column + 5,
                        "{:.2f}".format(cost["total_cost"]),
                        cell_amount_format,
                    )
                    row += 1

        except Exception as e:
            raise ValidationError(
                _(
                    "You are not able to print this report please contact your "
                    "administrator : %s " % str(e)
                )
            )
        workbook.close()
        file_name = "%s_%s_to_%s.xlsx" % (self.name, self.start_date, self.end_date)
        self.write(
            {"filename": file_name, "excel_file": base64.encodebytes(fp.getvalue())}
        )
        fp.close()
        return {
            "name": _("HR Transaction Report"),
            "type": "ir.actions.act_window",
            "res_model": "hr.transaction.report",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "target": "new",
        }
