# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    employee_status = fields.Selection(selection_add=[('probation', 'Probation')], default='probation', ondelete={'probation': 'cascade'})
    effective_date = fields.Date(string='Effective Date', copy=False)

    @api.onchange('department_id', 'date_of_join')
    def onchange_department_and_join_date(self):
        self.effective_date = False
        if self.department_id and self.date_of_join:
            probation_duration = self.env['ir.config_parameter'].sudo().get_param('saudi_hr_probation.probation_duration') or 3
            self.effective_date = self.date_of_join + relativedelta(months=self.department_id and self.department_id.probation_duration or probation_duration)
