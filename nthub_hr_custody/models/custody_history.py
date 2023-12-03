from odoo import models,fields,api
class CustodyHistory(models.Model):
    _name = 'hr.custody.history'

    custody_id = fields.Many2one('hr.custody')
    employee_id = fields.Many2one('hr.employee')
    date = fields.Date()
    state = fields.Selection([('active','Active'),('done','Done')])
