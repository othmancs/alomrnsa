# -*- coding: utf-8 -*-
from odoo import fields, models


class MedicalInsuranceType(models.Model):
    _name = "hr.medical.insurance.type"
    _description = "HR Medical Insurance Type"

    name = fields.Char(string="Name", required=True, translate=True, copy=False)
    code = fields.Char(string="Code", copy=False)
    amount = fields.Float(string="Amount", required=True, copy=False)
