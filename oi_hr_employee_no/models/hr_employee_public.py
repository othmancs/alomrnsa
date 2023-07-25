'''
Created on Jul 13, 2020

@author: Zuhair Hammadi
'''
from odoo import models, fields

class HREmployee (models.Model):
    _inherit = 'hr.employee.public'
        
    employee_no = fields.Char('Employee Company ID', readonly=True) 
