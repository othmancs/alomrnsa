# Author: Damien Crier
# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# Copyright 2021 Tecnativa - João Marques
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class GeneralLedgerXslx(models.AbstractModel):
    _name = "report.a_f_r.report_general_ledger_xlsx"
    _description = "General Ledger XLSX Report"
    _inherit = "report.account_financial_report.abstract_report_xlsx"

    def _get_report_name(self, report, data=False):
        company_id = data.get("company_id", False)
        report_name = _("General Ledger")
        if company_id:
            company = self.env["res.company"].browse(company_id)
            suffix = " - {} - {}".format(company.name, company.currency_id.name)
            report_name = report_name + suffix
        return report_name

    def _get_report_columns(self, report):
        res = [
            {"header": _("Date"), "field": "date", "width": 11},
            {"header": _("Entry"), "field": "entry", "width": 18},
            {"header": _("Partner"), "field": "partner_name", "width": 25},
        ]
        if report.show_cost_center:
            res += [
                {
                    "header": _("Analytic Distribution"),
                    "field": "analytic_distribution",
                    "width": 20,
                },
            ]
        res += [
            {"header": _("Rec."), "field": "rec_name", "width": 15},
            {
                "header": _("Debit"),
                "field": "debit",
                "field_initial_balance": "initial_debit",
                "field_final_balance": "final_debit",
                "type": "amount",
                "width": 14,
            },
            {
                "header": _("Credit"),
                "field": "credit",
                "field_initial_balance": "initial_credit",
                "field_final_balance": "final_credit",
                "type": "amount",
                "width": 14,
            },
            {
                "header": _("Cumul. Bal."),
                "field": "balance",
                "field_initial_balance": "initial_balance",
                "field_final_balance": "final_balance",
                "type": "amount",
                "width": 14,
            },
        ]
        if report.foreign_currency:
            res += [
                {
                    "header": _("Amount cur."),
                    "field": "bal_curr",
                    "field_initial_balance": "initial_bal_curr",
                    "field_final_balance": "final_bal_curr",
                    "type": "amount_currency",
                    "width": 10,
                },
                {
                    "header": _("Cumul cur."),
                    "field": "total_bal_curr",
                    "field_initial_balance": "initial_bal_curr",
                    "field_final_balance": "final_bal_curr",
                    "type": "amount_currency",
                    "width": 10,
                },
            ]
        res_as_dict = {}
        for i, column in enumerate(res):
            res_as_dict[i] = column
        return res_as_dict

    def _generate_report_content(self, workbook, report, data, report_data):
        res_data = self.env[
            "report.account_financial_report.general_ledger"
        ]._get_report_values(report, data)
        general_ledger = res_data["general_ledger"]

        # For each account
        for account in general_ledger:
            self.write_array_title(
                account["code"] + " - " + res_data["accounts_data"][account["id"]]["name"],
                report_data,
            )

            if "list_grouped" not in account:
                self.write_array_header(report_data)
                self.write_initial_balance_from_dict(account, report_data)

                for line in account["move_lines"]:
                    self.write_line_from_dict(line, report_data)

                self.write_ending_balance_from_dict(account, report_data)

            else:
                for group_item in account["list_grouped"]:
                    self.write_array_title(group_item["name"], report_data)
                    self.write_array_header(report_data)
                    self.write_initial_balance_from_dict(group_item, report_data)

                    for line in group_item["move_lines"]:
                        self.write_line_from_dict(line, report_data)

                    self.write_ending_balance_from_dict(group_item, report_data)
                    report_data["row_pos"] += 1

            report_data["row_pos"] += 2

    def write_initial_balance_from_dict(self, my_object, report_data):
        label = _("Initial balance")
        return super().write_initial_balance_from_dict(my_object, label, report_data)

    def write_ending_balance_from_dict(self, my_object, report_data):
        label = _("Ending balance")
        return super().write_ending_balance_from_dict(my_object, label, report_data)
