from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    partner_id = fields.Many2one('res.partner', string='Contact', readonly=True)

    @api.model
    def create(self, vals):
        employee = super(HrEmployee, self).create(vals)

        if not employee.partner_id:
            partner_vals = {
                'name': employee.name,
                'email': employee.work_email,
                'phone': employee.work_phone,
                'mobile': employee.mobile_phone,
                'company_type': 'person',
                'employee': True,
            }
            partner = self.env['res.partner'].create(partner_vals)
            employee.partner_id = partner.id

        return employee
