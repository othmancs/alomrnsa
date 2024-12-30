
import time

# from numpy import product
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

class ProductInvoiceXlsx(models.AbstractModel):
    _name = "report.odoo_custom_reports.product_invoice_xlsx"
    _inherit = 'report.report_xlsx.abstract'
    _description = "Product Invoice Xlsx Report"

    @api.model
    def generate_xlsx_report(self, workbook, data, products):
    
        bold = workbook.add_format({'bold':True})
        sheet=workbook.add_worksheet('Products Invoice Report')
        row = 0
        col = 0
                        
        sheet.write(row, col, 'Invoice Number', bold)

        col += 1
        sheet.write(row, col, 'Invoice date', bold)

        col += 1
        sheet.write(row, col, 'Customer', bold)

        col += 1
        sheet.write(row, col, 'Product', bold)

        col += 1
        sheet.write(row, col, 'Description', bold)

        col += 1
        sheet.write(row, col, 'Quantity', bold)

        col += 1
        sheet.write(row, col, 'Unit Of Measure', bold) 

        col += 1
        sheet.write(row, col, 'Unit Price', bold)   

        col += 1
        sheet.write(row, col, 'Amount', bold)

    
        for obj in data['products']:  
            row += 1  
            sheet.write(row, col - 8, obj['move_id'][1])
            sheet.write(row, col - 7, obj['date'])
            sheet.write(row, col - 6, obj['partner_id'][1])
            sheet.write(row, col - 5, obj['name'])
            # sheet.write(row, col - 4, obj['invoice_line_ids'][1])
            sheet.write(row, col - 3, obj['quantity'])
            # sheet.write(row, col - 2, obj['product_id'])
            sheet.write(row, col - 1, obj['price_unit'])
            sheet.write(row, col, obj['price_total'])
            # if(obj['journal_id'][0] == 2):

        