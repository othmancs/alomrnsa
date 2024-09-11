# -*- coding: utf-8 -*-

import io
import xlrd
import babel
import logging
import tempfile
import binascii
from io import StringIO
from datetime import date, datetime, time
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, UserError, ValidationError
_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ImportEmployee(models.TransientModel):
    _name = 'import.employee'
    _description = 'Import Employee'

    file_type = fields.Selection([('CSV', 'CSV File'),('XLS', 'XLS File')],string='File Type', default='CSV')
    file = fields.Binary(string="Upload File")

    def import_employee(self):
        if not self.file:
            raise ValidationError(_("Please Upload File to Import Employee !"))

        if self.file_type == 'CSV':
            line = keys = ['name','job_title','mobile_phone','work_phone','work_email','department_id','address_id','gender','birthday', 'color', 'marital', 'identification_id', 'sinid', 'passport_id', 'notes', 'last_name', 'middle_name', 'is_benefits_enrolled', 'timesheet_cost']
            try:
                csv_data = base64.b64decode(self.file)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
            except Exception:
                raise ValidationError(_("Please Select Valid File Format !"))
                
            values = {}
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        res = self.create_employee(values)
        else:
            try:
                file = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                file.write(binascii.a2b_base64(self.file))
                file.seek(0)
                values = {}
                workbook = xlrd.open_workbook(file.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise ValidationError(_("Please Select Valid File Format !"))

            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
                else:
                    line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    values.update( {
                            'name':line[0],
                            'job_title': line[1],
                            'mobile_phone': line[2],
                            'work_phone':line[3],
                            'work_email':line[4],
                            'department_id':line[5],
                            'address_id':line[6],
                            'gender':line[7],
                            'birthday':line[8],
                            'color': line[9],
                            'marital': line[10],
                            'identification_id': line[11],
                            'sinid': line[12],
                            'passport_id': line[13],
                            'notes': line[14],
                            'last_name': line[15],
                            'middle_name': line[16],
                            'is_benefits_enrolled': line[17],
                            'timesheet_cost': line[18]
                            })
                    res = self.create_employee(values)


    def create_employee(self, values):
        employee = self.env['hr.employee']
        department_id = self.get_department(values.get('department_id'))
        address_id = self.get_address(values.get('address_id'))
        birthday = self.get_birthday(values.get('birthday'))
        marital = False
        if values.get('gender') == 'Male':
            gender ='male'
        elif values.get('gender') == 'male':
            gender ='male'
        elif values.get('gender') == 'Female':
            gender ='female'
        elif values.get('gender') == 'female':
            gender ='female'
        elif values.get('gender') == 'Other':
            gender ='other'
        elif values.get('gender') == 'other':
            gender ='other'
        else:
            gender = 'male'

        if values.get('marital') == 'Single':
            marital = 'single'
        elif values.get('marital') == 'Married':
            marital = 'married'
        elif values.get('marital') == 'Legal Cohabitant':
            marital = 'cohabitant'
        elif values.get('marital') == 'Widower':
            marital = 'widower'
        elif values.get('marital') == 'Divorced':
            marital = 'divorced'
        
        vals = {
                'name' : values.get('name'),
                'job_title' : values.get('job_title'),
                'mobile_phone' : values.get('mobile_phone'),
                'work_phone' : values.get('work_phone'),
                'work_email' : values.get('work_email'),
                'department_id' : department_id.id,
                'address_id' : address_id.id,
                'gender' : gender,
                'birthday' : birthday,
                'color': values.get('color'),
                'marital': marital,
                'identification_id': values.get('identification_id'),
                'sinid': values.get('sinid'),
                'passport_id': values.get('passport_id'),
                'notes': values.get('notes'),
                'last_name': values.get('last_name'),
                'middle_name': values.get('middle_name'),
                'is_benefits_enrolled': values.get('is_benefits_enrolled'),
                'timesheet_cost': values.get('timesheet_cost')
                }


        if values.get('name')=='':
            raise UserError(_('Employee Name is Required !'))
        if values.get('department_id')=='':
            raise UserError(_('Department Field can not be Empty !'))

        res = employee.create(vals)
        return res


    def get_department(self, name):
        department = self.env['hr.department'].search([('name', '=', name)],limit=1)
        if department:
            return department
        else:
            return department.create({'name': name})

    def get_address(self, name):
        address = self.env['res.partner'].search([('name', '=', name)],limit=1)
        if address:
            return address
        else:
            return address.create({'name': name})

    def get_birthday(self, date):
        try:
            birthday = datetime.strptime(date, '%Y/%m/%d')
            return birthday
        except Exception:
            raise ValidationError(_('Wrong Date Format ! Date Should be in format YYYY/MM/DD'))
