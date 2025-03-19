from odoo import models


class AccountReportXlsx(models.AbstractModel):
    _name = 'report.kb_account_reports.report_account_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        domain = [('date', '<=', data['end_date']), ('date', '>=', data['start_date']), ('account_id', '=', data['account_id'])]
        if data['state'] == 'draft':
            state = 'Unposted'
            domain.append(('parent_state', '=', 'draft'))
        elif data['state'] == 'posted':
            state = 'Posted'
            domain.append(('parent_state', '=', 'posted'))
        else:
            state = 'All'
        move_line_ids = self.env['account.move.line'].search(domain, order='date asc, move_id DESC')
        
        domain = [ ('date', '<', data['start_date']), ('account_id', '=', data['account_id'])]
        if data['state'] == 'draft':
            state = 'Unposted'
            domain.append(('parent_state', '=', 'draft'))
        elif data['state'] == 'posted':
            state = 'Posted'
            domain.append(('parent_state', '=', 'posted'))
        else:
            state = 'All'
        move_balance = self.env['account.move.line'].search(domain)
        
        
        header_merge_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter',
                                                   'font_size': 10, 'bg_color': '#D3D3D3', 'border': 1})
        header_data_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                  'font_size': 10, 'border': 1})
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:B', 18)
        worksheet.set_column('C:H', 12)
        worksheet.write(2, 0, 'Date From', header_merge_format)
        worksheet.write(3, 0, data.get('start_date'), header_data_format)
        worksheet.write(2, 1, 'Date To', header_merge_format)
        worksheet.write(3, 1, data.get('end_date'), header_data_format)
        worksheet.write(2, 2, 'Status', header_merge_format)
        worksheet.write(3, 2, state, header_data_format)
        worksheet.write(2, 3, 'Account', header_merge_format)
        worksheet.write(3, 3, data.get('account_name'), header_data_format)

        worksheet.write(5, 0, 'Date', header_merge_format)
        worksheet.write(5, 1, 'Reference', header_merge_format)
        worksheet.merge_range(5, 2, 5, 3, "Partner", header_merge_format)
        worksheet.write(5, 4, 'Debit', header_merge_format)
        worksheet.write(5, 5, 'Credit', header_merge_format)
        worksheet.write(5, 6, 'Balance', header_merge_format)
        rows = 6
        balance = 0
        for x in move_balance:
            balance = x.debit - x.credit + balance
        worksheet.write(rows, 0, "", header_data_format)
        worksheet.write(rows, 1, "", header_data_format)
        worksheet.merge_range(rows, 2, rows, 3, "Balance", header_data_format)
        if balance > 0:
            worksheet.write(rows, 4, balance, header_data_format)
        else:
            worksheet.write(rows, 4, balance * 0, header_data_format)
        if balance < 0:
            worksheet.write(rows, 5, balance * -1, header_data_format)
        else:
            worksheet.write(rows, 5, balance * 0, header_data_format)
        worksheet.write(rows, 6, "" , header_data_format)
        rows += 1
        for line in move_line_ids:
            print(type(line.date))
            worksheet.write(rows, 0, str(line.date.strftime("%d-%m-%Y")), header_data_format)
            worksheet.write(rows, 1, line.move_id.name, header_data_format)
            worksheet.merge_range(rows, 2, rows, 3, line.partner_id.name, header_data_format)
            worksheet.write(rows, 4, line.debit, header_data_format)
            worksheet.write(rows, 5, line.credit, header_data_format)
            balance = line.debit - line.credit + balance
            worksheet.write(rows, 6,balance , header_data_format)
            rows += 1
        workbook.close()
