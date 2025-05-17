'''
Created on Nov 5, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

class Partner(models.Model):
    _inherit = "res.partner"

    employee_ids = fields.One2many('hr.employee', 'address_home_id', string='Related Employee')    
    employee = fields.Boolean(compute = '_calc_employee', compute_sudo = True, store = True, string='Is Employee')
    
    @api.depends('employee_ids')
    def _calc_employee(self):
        for record in self:
            record.employee = bool(record.employee_ids)            