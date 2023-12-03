from odoo import models, fields, api, _


class HrJob(models.Model):
    _inherit = 'hr.job'

    property_ids = fields.One2many('custody.property','job_id')

