# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from datetime import datetime
from odoo import models, api,fields


class ExportCustomerPricelistReport(models.AbstractModel):
	_name = 'report.bi_employee_payslip_report.report_emp_payslip'
	_description = 'Employee Payslip Report'

	

	def _get_payslip_details(self, payslip_ids):
		main=[]
		final = []
		new = {}
		no = 1
		
		b_lst = []
		a_lst = []
		g_lst = []
		d_lst = []
		n_lst = []
		
		
		lable = self._get_payslip_lable(payslip_ids)[0]
		for payslip in payslip_ids:
			values = {}
			category = []
			not_category = []
			if lable.get('no'):
				values['NO'] = no,
			if lable.get('payslip_ref'):
				values['Payslip_Ref'] = payslip.number or '',
			if lable.get('employee'):
				values['Employee'] = payslip.employee_id.name or '',
			if lable.get('designation'):
				values['Designation'] = payslip.employee_id.job_id.name or '',
			if lable.get('period'):
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

		for mn in main:
			if 'BASIC' in mn.keys():
				b_lst = self.get_sum_of_values('BASIC', b_lst, mn)
			
			if 'ALW' in mn.keys():
				a_lst = self.get_sum_of_values('ALW', a_lst, mn)
				
			if 'GROSS' in mn.keys():
				g_lst = self.get_sum_of_values('GROSS', g_lst, mn)
				
			if 'DED' in mn.keys():
				d_lst = self.get_sum_of_values('DED', d_lst, mn)
				
			if 'NET' in mn.keys():
				n_lst = self.get_sum_of_values('NET', n_lst, mn)

		
		new['basic_total'] = b_lst
		new['awl_total'] = a_lst
		new['gross_total'] = g_lst
		new['deduction_total'] = d_lst
		new['net_total'] = n_lst
		main.append(new)
		return main


	def get_sum_of_values(self, name_test=False, a=[], mn={}):
		val = mn.get(name_test)
		if len(a) == len(val):
			return [sum(x) for x in zip(a, val)]
		else:
			return val




	def _get_payslip_lable(self, payslip_ids):
		dict = {}
		lines=[dict]
		category = []
		main_sub = []
		for payslip in payslip_ids:
			for line in payslip.line_ids:
				subcategory = []
				dict['no'] = 'NO #'
				dict['payslip_ref'] = 'Payslip Ref'
				dict['employee'] = 'Employee'
				dict['designation'] = 'Designation'
				dict['period'] = 'Period'
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
							if i.lower()[:3] == line.category_id.name.lower()[:3]:
								for r in remaining:
									main_sub.append(r)
									dict[i].append(r)
		return lines
	
	@api.model
	def _get_report_values(self, docids, data=None):
		payslip_ids = self.env['hr.payslip'].browse(data['ids'])
		docargs = {
				   'doc_model': 'export.customer.pricelist',
				   'data': data,
				   'docs': payslip_ids,
				   'get_payslip_details':self._get_payslip_details(payslip_ids),
				   'get_payslip_lable':self._get_payslip_lable(payslip_ids),
				   }
		return docargs

