# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import datetime
import xlsxwriter
import base64
import io
from io import BytesIO
import tempfile
import csv
from io import StringIO


class EmpPayslipReport(models.TransientModel):
    _name = "emp.payslip.report"
    _description="EmpPayslip Report"

    file = fields.Binary("Download File")
    file_name = fields.Char(string="File Name")
    file_type = fields.Selection([('pdf', 'PDF'), ('xls', 'XLS')
                                  ], 'File Type', default="xls")
    
    
    
    
    def get_sum_of_values(self, name_test=False, a=[], mn={}):
        val = mn.get(name_test)
        if len(a) == len(val):
            return [sum(x) for x in zip(a, val)]
        else:
            return val
    

    def employee_payslip_xls(self):
        if self.file_type == 'pdf':
            self.ensure_one()
            [data] = self.read()
            active_ids = self.env.context.get('active_ids', [])
            payslip = self.env['hr.payslip'].browse(active_ids)
            datas = {
                'ids': active_ids,
                'model': 'emp.payslip.report ',
                'form': data
            }
            return self.env.ref('bi_employee_payslip_report.action_report_export_emp_payslip').report_action(self,data=datas)




        elif self.file_type == 'xls':
            name_of_file = 'Export Payslip Report.xls'
            file_path = 'Export Payslip Report' + '.xls'
            workbook = xlsxwriter.Workbook('/tmp/' + file_path)
            worksheet = workbook.add_worksheet('Export Payslip Report')

            header_format = workbook.add_format(
                {'bold': True, 'valign': 'vcenter', 'font_size': 16, 'align': 'center'})
            title_format = workbook.add_format(
                {'border': 1, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'font_size': 14,
                 'bg_color': '#D8D8D8'})
            cell_wrap_format_bold = workbook.add_format(
                {'border': 1, 'bold': True, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'center',
                 'font_size': 12})  ##E6E6E6
            cell_wrap_format = workbook.add_format(
                {'border': 1, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'left', 'font_size': 12, 'align': 'center', 'text_wrap': True })  ##E6E6E6
            
            
            sub_cell_wrap_format_bold = workbook.add_format({'border': 1, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'center',
                 'font_size': 12, 'text_wrap': True})
            
            worksheet.set_row(1, 30)  # Set row height
            worksheet.set_row(4, 50)
            
            # Merge Row Columns
            TITLEHEDER = 'تقرير الراتب'

            worksheet.set_column(0, 0, 3)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 3, 25)
            worksheet.set_column(4, 4, 25)
            worksheet.set_column(5, 15, 20)

            worksheet.merge_range(1, 1, 1, 7, TITLEHEDER, header_format)
            rowscol = 1
            
            active_ids = self.env.context.get('active_ids', [])
            payslip_ids = self.env['hr.payslip'].browse(active_ids)
            
            worksheet.merge_range(3, 0, 4, 0, '#', cell_wrap_format_bold)
            worksheet.merge_range(3, 1, 4, 1, 'رقم سلب الراتب', cell_wrap_format_bold)
            worksheet.merge_range(3, 2, 4, 2, 'اسم الموظف', cell_wrap_format_bold)
            # worksheet.merge_range(3, 3, 4, 3, 'Designation', cell_wrap_format_bold)
            worksheet.merge_range(3, 4, 4, 4, 'الفترة', cell_wrap_format_bold)
            
            
            #For the get Lables
            print(payslip_ids)
            dict = {}
            lines=[dict]
            category = []
            main_sub = []
            for payslip in payslip_ids:
                for line in payslip.line_ids:
                    subcategory = []
                    category_id = line.category_id
                    all_subcategory = self.env['hr.payslip.line'].search([('category_id', '=', category_id.id),('slip_id','=', payslip.id)])
                    if line.category_id.code not in category:
                        category.append(line.category_id.code)
                        if all_subcategory:
                            for i in all_subcategory:
                                subcategory.append(i.name)
                                main_sub.append(i.name)
                        dict[line.category_id.code] = subcategory
                    else:
                        remaining=[]
                        if all_subcategory:
                            for i in all_subcategory:
                                if i.name not in main_sub:
                                    remaining.append(i.name)
                        if remaining:
                            for i, j in dict.items():
                                if i.lower()[:3] == line.category_id.name.lower()[:3] :
                                    for r in remaining:
                                        main_sub.append(r)
                                        dict[i].append(r)
            
            #For Print the Lable 
            for line in lines:
                start_col = 5
                row = 3
                col = 5
                
                if 'BASIC' in line.keys():
                    val = len(line.get('BASIC'))
                    values = line.get('BASIC')
                    if val > 1:
                        worksheet.merge_range(row,start_col,row,start_col + (val - 1), 'اساسي' , cell_wrap_format_bold)
                        start_col = start_col + val
                        for i in values:
                            worksheet.write(4, col, i ,sub_cell_wrap_format_bold)
                            col+=1
                    else:
                        worksheet.write(row,start_col,'اساسي',cell_wrap_format_bold)
                        start_col = start_col + 1
                        
                        worksheet.write(4, col, values[0] ,sub_cell_wrap_format_bold)
                        col+=1
                
                if 'ALW' in line.keys():
                    val = len(line.get('ALW'))
                    values  = line.get('ALW')
                    
                    if val > 1:
                        worksheet.merge_range(row,start_col,row,start_col + (val - 1), 'اضافي' , cell_wrap_format_bold)
                        start_col = start_col + val
                        for i in values:
                            worksheet.write(4, col, i ,sub_cell_wrap_format_bold)
                            col+=1
                    else:
                        worksheet.write(row,start_col,'Allowance',cell_wrap_format_bold)
                        start_col = start_col + 1
                        
                        worksheet.write(4, col, values[0] ,sub_cell_wrap_format_bold)
                        col+=1
                
                if 'GROSS' in line.keys():
                    val = len(line.get('GROSS'))
                    values  = line.get('GROSS')
                    
                    if val > 1:
                        worksheet.merge_range(row,start_col,row,start_col + (val - 1), 'اجمالي' , cell_wrap_format_bold)
                        start_col = start_col + val
                        for i in values:
                            worksheet.write(4, col, i ,sub_cell_wrap_format_bold)
                            col+=1
                    else:
                        worksheet.write(row,start_col,'Gross',cell_wrap_format_bold)
                        start_col = start_col + 1
                        worksheet.write(4, col, values[0] ,sub_cell_wrap_format_bold)
                        col+=1
                        
                if 'DED' in line.keys():
                    val = len(line.get('DED'))
                    values  = line.get('DED')
                    
                    if val > 1:
                        worksheet.merge_range(row,start_col,row,start_col + (val - 1), 'Deduction' , cell_wrap_format_bold)
                        start_col = start_col + val
                        for i in values:
                            worksheet.write(4, col, i ,sub_cell_wrap_format_bold)
                            col+=1
                        
                    else:
                        worksheet.write(row,start_col,'Deduction',cell_wrap_format_bold)
                        start_col = start_col + 1
                        worksheet.write(4, col, values[0] ,sub_cell_wrap_format_bold)
                        col+=1
                        
                         
                         
                if 'NET' in line.keys():
                    val = len(line.get('NET'))
                    values  = line.get('NET')
                   
                    if val > 1:
                        worksheet.merge_range(row,start_col,row,start_col + (val - 1), 'صافي' , cell_wrap_format_bold)
                        start_col = start_col + val
                        for i in values:
                            worksheet.write(4, col, i ,sub_cell_wrap_format_bold)
                            col+=1
                    else:
                        worksheet.write(row,start_col,'Net',cell_wrap_format_bold)
                        start_col = start_col + 1
                        worksheet.write(4, col, values[0] ,sub_cell_wrap_format_bold)
                        col+=1
                       
                       
                       
            
            
            #For Print the values
            #For the get Values of lable
            main=[]
            final = []
            new = {}
            no = 1
            
            lable = lines[0]
            for payslip in payslip_ids:
                values = {}
                category = []
                not_category = []
                values['NO'] = no,
                values['Payslip_Ref'] = payslip.number or '',
                values['Employee'] = payslip.employee_id.name or '',
                # values['Designation'] = payslip.employee_id.job_id.name or '',
                values['Period'] = str(payslip.date_from) +  '  to  ' +str(payslip.date_to),
                lines = self.env['hr.payslip.line'].search([('slip_id','=', payslip.id)])
                all_category = lines.mapped('category_id.code')
                sub_categ = lines.mapped('name')
                temp = []
                for i , j in lable.items():
                    if i not in ['no', 'payslip_ref', 'employee', 'designation', 'period']:
                        if i in all_category:
                            present_categ = []
                            for sub in j:
                                if sub in sub_categ:
                                    for line in lines:
                                        if sub == line.name:
                                            present_categ.append(line.total)
                                            temp.append(line.total)
                                else:
                                    present_categ.append(0.0)
                                    temp.append(0.0)
                            values[i] = present_categ
                        else:
                            not_present_categ = []
                            for k in j:
                                not_present_categ.append(0.0)
                                temp.append(0.0)
                            values[i] = not_present_categ    
                no = no + 1
                main.append(values)
            
            
            
            #For get the values
            end_row = row
            row = 6
            for value in main:
                col = 0
                row = row
                list = ['NO', 'Payslip_Ref', 'Employee', 'Designation', 'Period', 'BASIC', 'ALW', 'GROSS', 'DED', 'NET']
                for l in list:
                    if l in value.keys():
                        data  = value.get(l)
                        for r in data:
                            worksheet.write(row,col, r, cell_wrap_format)
                            col+=1
                row+=1
                end_row = row
            
            
            #For Get the Total
            total_row = end_row + 1
            list = ['BASIC', 'ALW', 'GROSS', 'DED', 'NET']
            coln = 5
            for l in list:
                lst = []
                for mn  in main:
                    if l in mn.keys():
                        lst = self.get_sum_of_values(l, lst, mn)
                        
                for r in lst:
                    worksheet.write(total_row,coln, r, cell_wrap_format_bold)
                    coln +=1
            
            worksheet.merge_range(total_row, 3, total_row, 4, 'Total', cell_wrap_format_bold)

            workbook.close()
            export_id = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())
            result_id = self.env['emp.payslip.report'].create({'file': export_id, 'file_name': name_of_file})
            return {
                'name': 'Export Payslip Report',
                'view_mode': 'form',
                'res_id': result_id.id,
                'res_model': 'emp.payslip.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
