'''
Created on Nov 6, 2018

@author: Zuhair Hammadi
'''
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError

class Employee(models.Model):
    _inherit = "hr.employee"
    
    @api.onchange('address_home_id')
    def _on_change_address_home_id(self):
        if self.address_home_id and self.user_id.partner_id != self.address_home_id:
            self.user_id = self.address_home_id.user_ids[:1]
            
    @api.onchange('user_id')
    def _on_change_user_id(self):
        if self.user_id and self.user_id.partner_id != self.address_home_id:
            self.address_home_id = self.user_id.partner_id            
    
    @api.constrains('user_id', 'address_home_id') 
    def _check_user_id(self):
        for record in self:
            if record.user_id and record.address_home_id:
                if record.user_id.partner_id != record.address_home_id:
                    raise ValidationError(_('User and Private Address not match'))
            if record.user_id and record.user_id.employee_ids != record:
                raise ValidationError(_('User %s already link to an employee' % (record.user_id.name)))           
                                    
    @api.constrains('address_home_id') 
    def _check_address_home_id(self):
        for record in self:
            if record.address_home_id:
                if record.address_home_id.employee_ids != record:
                    raise ValidationError(_('Contact %s already link to an employee' % (record.address_home_id.name)))                