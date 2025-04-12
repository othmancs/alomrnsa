# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    iqama_number = fields.Char(
        string='IQAMA Number',
        related='employee_id.iqama_number',
        readonly=True,
        store=True,
        help="Employee's IQAMA number",
        exportable=True  # هذا السطر يضمن أن الحقل قابل للتصدير
    )