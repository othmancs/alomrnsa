# Part of Odoo. See LICENSE file for full copyright and licensing details.

import xlwt
import base64
from io import StringIO
from odoo import api, fields, models, _
import platform


class PayslipReportOut(models.Model):
    _name = 'payslip.report.out'
    _description = 'Payslip report'

    payslip_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Payslip Excel Report', readonly=True)


class WizardWizards(models.Model):
    _name = 'wizard.reports'
    _description = 'Payslip wizard'

    def action_payslip_report(self):
        custom_value = {}
        label_lists = ['PO', 'POR', 'CLIENTREF', 'BARCODE', 'DEFAULTCODE', 'NAME', 'QTY', 'VENDORPRODUCTCODE', 'TITLE',
                       'PARTNERNAME', 'EMAIL', 'PHONE', 'MOBILE', 'STREET', 'STREET2', 'ZIP', 'CITY', 'COUNTRY']
        order = self.env['hr.payslip'].browse(self._context.get('active_ids', list()))
        workbook = xlwt.Workbook()
        s_no = 0
        sheet = workbook.add_sheet('Payslip details')
        style0 = xlwt.easyxf(
            'font: name Times New Roman bold on;borders:left thin, right thin, top thin, bottom thin;align: horiz center;',
            num_format_str='#,##0.00')
        style1 = xlwt.easyxf(
            'font:bold True; borders:left thin, right thin, top thin, bottom thin;align: horiz center;',
            num_format_str='#,##0.00')

        sheet.write_merge(0, 0, 0, 0, 'S. No', style1)
        sheet.write_merge(0, 0, 1, 2, 'Employee ID', style1)
        sheet.write_merge(0, 0, 3, 4, 'Designation', style1)
        sheet.write_merge(0, 0, 5, 6, 'Bank Name', style1)
        sheet.write_merge(0, 0, 7, 8, 'IFSC Code', style1)
        sheet.write_merge(0, 0, 9, 10, 'Account No', style1)
        sheet.write_merge(0, 0, 11, 12, 'Total', style1)

        s_no = 1
        n = 0;
        m = 0

        for rec in order:
            custom_value['employee_id'] = rec.employee_id.name
            custom_value['job'] = rec.employee_id.job_title
            custom_value['bank_name'] = rec.employee_id.bank_account_id.bank_id.name
            custom_value['ifsc'] = rec.employee_id.bank_account_id.bank_id.bic
            custom_value['account_no'] = rec.employee_id.bank_account_id.acc_number
            if len(order.line_ids) > 1:
                for line in rec.line_ids:
                    if line.code == 'NET':
                        custom_value['net'] = line.amount

            sheet.write_merge(n + 1, n + 1, m, m, str(s_no), style0)
            sheet.write_merge(n + 1, n + 1, m + 1, m + 2, custom_value['employee_id'], style0)
            sheet.write_merge(n + 1, n + 1, m + 3, m + 4, custom_value['job'], style0)
            sheet.write_merge(n + 1, n + 1, m + 5, m + 6, custom_value['bank_name'], style0)
            sheet.write_merge(n + 1, n + 1, m + 7, m + 8, custom_value['ifsc'], style0)
            sheet.write_merge(n + 1, n + 1, m + 9, m + 10, custom_value['account_no'], style0)
            for line in rec.line_ids:
                if line.code == 'NET':
                    sheet.write_merge(n + 1, n + 1, m + 11, m + 12, custom_value['net'], style0)
            s_no = s_no + 1;
            n += 1;

        datas = []
        output = StringIO()
        label = ';'.join(label_lists)
        output.write(label)
        output.write("\n")

        for data in datas:
            record = ';'.join(data)
            output.write(record)
            output.write("\n")
        data = base64.b64encode(bytes(output.getvalue(), "utf-8"))

        if platform.system() == 'Linux':
            filename = ('/tmp/Payslip Report' + '.xls')
        else:
            filename = ('Payslip Report' + '.xls')

        workbook.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        # out = base64.encodestring(file_data)
        out = base64.encodebytes(file_data)

        # Files actions
        attach_vals = {
            'payslip_data': 'Payslip Report' + '.xls',
            'file_name': out,
        }

        act_id = self.env['payslip.report.out'].create(attach_vals)
        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'payslip.report.out',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
