# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
import base64
from odoo.tools import groupby
from datetime import datetime


class EmployeeInfo(http.Controller):

    @http.route('/employee/public_directory', auth='user', type='http', website=True, csrf=False)
    def get_employee_public_directory(self, **kw):
        # data = {}
        directory_list = []
        Employees = request.env['hr.employee'].sudo().search([('add_user_company_dir', '=', True)])
        for job, emps in groupby(Employees, lambda emp: emp.job_id):
            directory_list.append({job: emps})
        return request.render('saudi_hr.employee_public_directory', {'data': directory_list})

    @http.route('/employee/pinfo/<string:access_tokeen>', auth='user', type='http', website=True, csrf=False)
    def employee_fill_info(self, access_tokeen, **kw):
        employee = request.env['hr.employee'].sudo().search([('personal_access_token', '=', access_tokeen),
                                                            ('user_id', '=', request.env.user.id)], limit=1)
        countries = request.env['res.country'].sudo().search([])
        partners = request.env['res.partner'].sudo().search([])
        certificates = request.env['education.certificate'].sudo().search([])
        studies = request.env['education.study'].sudo().search([])
        schools = request.env['education.school'].sudo().search([])
        languages = request.env['res.lang'].sudo().search([('active', '=', True)])
        countries = request.env['res.country'].sudo().search([])
        degree_programs = request.env['hr.recruitment.degree'].sudo().search([])
        if employee:
            return request.render('saudi_hr.employee_fill_private_info', {'employee': employee,
                                                                        'countries': countries,
                                                                        'partners': partners,
                                                                        'certificates': certificates,
                                                                        'degree_programs': degree_programs,
                                                                        'studies': studies,
                                                                        'schools':schools,
                                                                        'countries': countries,
                                                                        'emp_languages': languages})
        return request.render('saudi_hr.employee_error_private_info')

    def get_employee_fill_data(self, employee, kw):
        data = {}
        home_address_vals = {}
        home_address_key = {'address_home_street': 'street',
                            'address_home_street_two': 'street2',
                            'address_home_city': 'city',
                            'address_home_zip': 'zip',
                            'address_home_state_id': 'state_id',
                            'address_home_country_id': 'country_id'}
        for key, value in kw.items():
            try:
                if key in ['birthday', 'visa_expire', 'work_permit_expiration_date']:
                    splitted_value = value.split(' ')
                    if splitted_value and value != '':
                        datetime_object = datetime.strptime(splitted_value[0], '%m/%d/%Y')
                        data.update({key: datetime_object})
                elif key == 'has_work_permit':
                    attached_files = request.httprequest.files.getlist('has_work_permit')
                    if attached_files:
                        attached_file = attached_files[0].read()
                        data.update({'has_work_permit': base64.b64encode(attached_file)})
                elif key in ['address_home_street', 'address_home_street_two', 'address_home_city', 'address_home_zip']:
                    home_address_vals.update({home_address_key[key]: value})
                elif key in ['address_home_country_id', 'address_home_state_id'] and value:
                    home_address_vals.update({home_address_key[key]: int(value)})
                elif key == 'name_of_nominee':
                    if employee.sudo().nominee_id:
                        employee.nominee_id.sudo().write({'name': value})
                    else:
                        nominee = employee.nominee_id.sudo().create({'name': value})
                        data.update({'nominee_id': nominee.id})
                else:
                    data.update({key: eval(value)})
            except Exception as e:
                data.update({key: value})
        if employee:
            if employee.sudo().address_home_id:
                employee.sudo().address_home_id.sudo().write(home_address_vals)
            else:
                home_address_vals.update({'name': employee.display_name})
                address_id = employee.sudo().address_home_id.sudo().create(home_address_vals)
                data.update({'address_home_id': address_id.id})
        return data

    @http.route('/employee/submit', auth='user', type='http', website=True, csrf=False)
    def employee_fill_submit(self, **kw):
        if 'employee' in kw:
            employee = kw.pop('employee')
            Employee = request.env['hr.employee'].browse(eval(employee))
            data = self.get_employee_fill_data(Employee, kw)            
            if not Employee or not Employee.sudo().personal_access_token:
                return request.render('saudi_hr.employee_error_private_info')
            data.update({'personal_access_token': False})
            try:
                Employee.sudo().write(data)
            except Exception as e:
                return request.render('saudi_hr.employee_error_private_info_save', {'error': e})
        return request.render('saudi_hr.employee_sumbitted_private_info')
