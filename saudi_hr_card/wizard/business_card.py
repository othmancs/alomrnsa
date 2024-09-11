# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from PIL import Image
import io
from io import BytesIO
import xlsxwriter
import base64


class BusinessCard(models.TransientModel):
    _name = "business.card"
    _description = "Business Card"

    filename = fields.Char('File Name', size=64)
    excel_file = fields.Binary('Excel File')

    def print_business_card(self):
        employee_card_obj = self.env[self.env.context.get('active_model', False)]
        emp_card = employee_card_obj.browse(self.env.context.get('active_id', False))
        if emp_card.card_type != 'business':
            raise UserError(_('You can not print business card.'))
        filename = 'Business Card of %s.xlsx' % emp_card.employee_id.name
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Business card')
        worksheet.set_column('A:A', 2)
        worksheet.set_column('B:B', 3)
        worksheet.set_column('C:C', 8)
        worksheet.set_column('D:D', 7)
        worksheet.set_column('E:E', 7)
        worksheet.set_column('F:F', 7)
        worksheet.set_column('J:J', 8)
        worksheet.set_column('K:K', 3)
        name_head = workbook.add_format({
                    'bold': 1,
                    'align': 'left',
                    'valign': 'vleft',
                    'font_size': 12,
                    'font_name': 'Times New Roman'})
        detail_head = workbook.add_format({
                    'bold': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'font_size': 10,
                    'font_name': 'Times New Roman'})
        details_format = workbook.add_format({
                    'align': 'left',
                    'font_size': 10,
                    'valign': 'vleft',
                    'font_name': 'Times New Roman'})
        # arabic_name = workbook.add_format({
        #             'bold': 1,
        #             'align': 'right',
        #             'valign': 'vright',
        #             'font_size': 10,
        #             })
        # arabic_format = workbook.add_format({
        #             'align': 'right',
        #             'valign': 'vright',
        #             'font_size': 8,
        #             })

        if self.env.user.company_id.logo:
            im = Image.open(io.BytesIO(base64.b64decode(self.env.user.company_id.logo))).convert("RGB")
            im = im.resize((100, 50))
            im.save('/tmp/image.jpg', quality=90)
            worksheet.insert_image('C3', '/tmp/image.jpg', {'x_scale': 0.62, 'y_scale': 0.8})
            worksheet.insert_image('J21', '/tmp/image.jpg', {'x_scale': 0.62, 'y_scale': 0.8})

        row = 4
        col = 3
        worksheet.merge_range(row, col, row, col + 5, ' '.join([emp_card.employee_id.name or '',
                                                                emp_card.employee_id.middle_name or '',
                                                                emp_card.employee_id.last_name or '']),
                              name_head)
        row += 1
        worksheet.merge_range(row, col, row, col + 5, emp_card.employee_id.job_title or '', name_head)
        row += 2
        worksheet.merge_range(row, col, row, col + 2, emp_card.branch_id.company_name or '', details_format)
        worksheet.write(row, col + 3, 'Phone:', detail_head)
        worksheet.merge_range(row, col + 4, row, col + 5, emp_card.work_phone or '', details_format)
        row += 1
        worksheet.merge_range(row, col, row, col + 2, emp_card.branch_id.street or '', details_format)
        worksheet.write(row, col + 3, 'Mobile:', detail_head)
        worksheet.merge_range(row, col + 4, row, col + 5, emp_card.work_mobile or '', details_format)
        row += 1
        worksheet.merge_range(row, col, row, col + 2, emp_card.branch_id.street2 or '', details_format)
        row += 1
        worksheet.write(row, col, emp_card.branch_id.po_box_no or '', details_format)
        worksheet.write(row, col + 1, emp_card.branch_id.city or '', details_format)
        worksheet.write(row, col + 2, emp_card.branch_id.zip or '', details_format)
        row += 1
        worksheet.merge_range(row, col, row, col + 2, emp_card.branch_id.country or '', details_format)
        row += 2
        worksheet.merge_range(row, col, row, col + 2, emp_card.work_email or '', details_format)
        row += 8

        #arabic address details :

        # worksheet.merge_range(row, col, row, col + 5, emp_card.employee_id.arabic_name or '', arabic_name)
        # row += 1
        # worksheet.merge_range(row, col, row, col + 5, emp_card.employee_id.job_id
        #                       and emp_card.employee_id.job_id.arabic_name or '', arabic_name)
        # row += 2
        # worksheet.merge_range(row, col + 3, row, col + 5, emp_card.branch_id.company_arabic_name or '',
        #                       arabic_format)
        # worksheet.write(row, col + 2, 'هاتف', detail_head)
        # worksheet.merge_range(row, col, row, col + 1, emp_card.work_phone or '', arabic_format)
        # row += 1
        # worksheet.merge_range(row, col + 3, row, col + 5, emp_card.branch_id.arabic_street or '', arabic_format)
        # worksheet.write(row, col + 2, 'جوال', detail_head)
        # worksheet.merge_range(row, col, row, col + 1, emp_card.work_mobile or '', arabic_format)
        # row += 1
        # worksheet.merge_range(row, col + 3, row, col + 5, emp_card.branch_id.arabic_street2 or '', arabic_format)
        # row += 1
        # worksheet.write(row, col + 5, emp_card.branch_id.arabic_city or '', arabic_format)
        # worksheet.write(row, col + 4, emp_card.branch_id.zip or '', arabic_format)
        # row += 1
        # worksheet.merge_range(row, col + 5, row, col + 4, emp_card.branch_id.arabic_country or '', arabic_format)
        # row += 2
        # worksheet.merge_range(row, col + 5, row, col + 4, emp_card.work_email or '', arabic_format)
        row += 2
        workbook.close()
        export_id = self.env['business.card'].create({'excel_file': base64.encodebytes(fp.getvalue()),
                                                      'filename': filename})
        fp.close()

        return {
            'name': 'Business Card',
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'business.card',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }
