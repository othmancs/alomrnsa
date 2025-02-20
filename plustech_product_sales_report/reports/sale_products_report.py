# -- coding: utf-8 --
#################################################################################
# Author      : Plus Technology Co.Ltd. (<https://www.plustech-it.com//>)
# Copyright(c): 2024-Plus Technology Co. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
from odoo import api, models, _


class SalesProductsReport(models.AbstractModel):
    _name = "report.plustech_product_sales_report.sale_product_report"
    _description = "Sale Products Report"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        products = obj._query()
        date_from = obj.date_from
        date_to = obj.date_to
        header_title_format = workbook.add_format({
            'border': 0,
            'align': 'center',
            'font_color': '#0d084c',
            'bold': True,
            'valign': 'vcenter',
            'text_wrap': 'true',
        })
        header_title_format.set_text_wrap()
        header_title_format.set_font_size(18)

        header1_format = workbook.add_format({
            'border': 1,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': False,
            'valign': 'vcenter',
            'fg_color': '#808080'})
        header1_format.set_text_wrap()
        header1_format.set_font_size(12)

        header2_format = workbook.add_format({
            'border': 1,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': False,
            'valign': 'vcenter',
        })
        header2_format.set_text_wrap()
        header2_format.set_font_size(12)

        header3_format = workbook.add_format({
            'border': 1,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': True,
            'valign': 'vcenter',
            'fg_color': '#d8d8d8',
        })
        header3_format.set_text_wrap()
        header4_format = workbook.add_format({
            'border': 1,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'white',
            'bold': False,
            'valign': 'vcenter',
            'fg_color': '#454545'})
        header4_format.set_text_wrap()
        header4_format.set_font_size(12)
        worksheet = workbook.add_worksheet()

        worksheet.right_to_left()
        worksheet.set_column('A:A', 40)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_row(0, 20)
        worksheet.set_row(1, 20)
        worksheet.set_row(2, 25)
        worksheet.set_row(3, 25)

        row = 4
        subtotal_sum = 0
        discount_sum = 0
        after_sum = 0
        tax_sum = 0
        qty_sum = 0
        refund_sum = 0
        refund_qty_sum = 0

        for product in products:
            worksheet.set_row(row, 30)
            worksheet.write(row, 0, product.get('name', {}).get('ar_001') or product.get('name', {}).get(
                'en_US') or product.get('name', ''), header2_format)
            worksheet.write(row, 1, '{:,.2f}'.format(product['total_price_subtotal']), header2_format)
            subtotal_sum += product['total_price_subtotal']
            worksheet.write(row, 2, '{:,.2f}'.format(product['total_discount_amount']), header2_format)
            discount_sum += product['total_discount_amount']
            worksheet.write(row, 3, '{:,.2f}'.format(product['total_price_total']), header2_format)
            after_sum += product['total_price_total']
            worksheet.write(row, 4, '{:,.2f}'.format(product['total_tax_amount']), header2_format)
            tax_sum += product['total_tax_amount']
            worksheet.write(row, 5, product['total_quantity'], header2_format)
            qty_sum += product['total_quantity']
            worksheet.write(row, 6, '{:,.2f}'.format(product['list_price']), header2_format)
            worksheet.write(row, 7, '{:,.2f}'.format(product['refund_total_price_total']), header2_format)
            refund_sum += product['refund_total_price_total']
            worksheet.write(row, 8, product['refund_quantity'], header2_format)
            refund_qty_sum += product['refund_quantity']

            row += 1

        worksheet.merge_range('A1:I1', 'تقرير المبيعات بالاجمالي ', header3_format)
        worksheet.merge_range('B2:I2', 'الاجمالي ', header3_format)
        content = f'التاريخ\nمن: {date_from}\nالى: {date_to}'
        if date_from and date_to:
            worksheet.merge_range('A2:A4', content, header3_format)
        else:
            worksheet.merge_range('A2:A4', "منتجات", header3_format)
        worksheet.write(2, 1, 'الإجمالي قبل الخصم', header3_format)
        worksheet.write(2, 2, 'مبلغ الخصم', header3_format)
        worksheet.write(2, 3, 'الصافى بعد الخصم', header3_format)
        worksheet.write(2, 4, 'قيمة الضريبة', header3_format)
        worksheet.write(2, 5, 'الكمية المفوترة', header3_format)
        worksheet.write(2, 6, 'سعر البيع', header3_format)
        worksheet.write(2, 7, 'مبلغ المرتجع', header3_format)
        worksheet.write(2, 8, 'كمية المرتجع', header3_format)
        worksheet.write(3, 1, '{:,.2f}'.format(subtotal_sum), header2_format)
        worksheet.write(3, 2, '{:,.2f}'.format(discount_sum), header2_format)
        worksheet.write(3, 3, '{:,.2f}'.format(after_sum), header2_format)
        worksheet.write(3, 4, '{:,.2f}'.format(tax_sum), header2_format)
        worksheet.write(3, 5, '{:,.2f}'.format(qty_sum), header2_format)
        worksheet.write(3, 6, '', header2_format)
        worksheet.write(3, 7, '{:,.2f}'.format(refund_sum), header2_format)
        worksheet.write(3, 8, '{:,.2f}'.format(refund_qty_sum), header2_format)
