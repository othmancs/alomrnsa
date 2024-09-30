from odoo import models


class EndOfServiceReportXlsx(models.AbstractModel):
    _name = 'report.hr_contract.end_of_service_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('End of Service Report')

        # Headers for the report
        headers = ['Employee Name', 'Residence ID', 'Nationality', 'Employer', 'Settlement No', 'Settlement Date',
                   'Total Amount']
        row = 0
        col = 0
        for header in headers:
            sheet.write(row, col, header)
            col += 1

        # Fetch data to fill the report
        contract_records = self.env['hr.end_of_service_report'].search([('employee_id', '=', wizard.employee_id.id)])
        row += 1
        for record in contract_records:
            sheet.write(row, 0, record.employee_id.name)
            sheet.write(row, 1, record.residence_id)
            sheet.write(row, 2, record.nationality)
            sheet.write(row, 3, record.employer_name)
            sheet.write(row, 4, record.settlement_number)
            sheet.write(row, 5, str(record.settlement_date))
            sheet.write(row, 6, record.total_amount)
            row += 1
