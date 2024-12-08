# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    
    def action_payslip_done(self):
        result = super(HrPayslip, self).action_payslip_done()
        if result:
            self.contract_id.write({'state':'close'})
        return result


