from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    def create_employee_from_applicant(self):

        res = super(HrApplicant, self).create_employee_from_applicant()
        return res

    def action_show_custody(self):
        property_ids = self.job_id.property_ids.ids
        return {
            'name': "Custody Properties",
            'type': 'ir.actions.act_window',
            'res_model': 'custody.property',
            'view_mode': 'tree',

            # 'view_id': self.env.ref("emr_coverage.patient_custom_tree_view").id,
            'context': {'class_id': self.id},
            'domain': [('id', 'in', property_ids)],

            'view_id': self.env.ref("nthub_hr_custody.show_custody_property_tree_view").id,
            'context': {'employee_id': self.emp_id.id},

            'target': 'new'
        }
