'''
Created on Nov 26, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

class HREmployee (models.Model):
    _inherit = 'hr.employee'
        
    employee_no = fields.Char('Employee Company ID', copy = False) 
    
    _sql_constraints= [
            ('employee_no_unqiue', 'unique(company_id, employee_no)', 'Employee Company ID must be unique!')
    ]    
                
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        
        search_limit = limit
        sort_by_search_input = self.env['ir.config_parameter'].sudo().get_param('employee_name_search_sort_by_search_input') == 'True'
        if sort_by_search_input:
            search_limit = None
        
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit = search_limit)
        
        if name and sort_by_search_input:
            recs = recs.sorted(key = lambda rec : (1 if rec.name.lower().startswith(name.lower()) else 2, rec.name))
            
        recs = recs[:limit]    
        
        return recs.name_get()


    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('employee_no'):
                vals['employee_no'] = self.env['ir.sequence'].next_by_code(self._name)
        
        return super(HREmployee, self).create(vals_list)