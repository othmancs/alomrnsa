# -*- coding: utf-8 -*-
from odoo import models, fields

class RelatedModel(models.Model):
    _name = 'related.model'
    _description = 'Related Model'
    
    schedule_pay = fields.Char(string="Payment Schedule")
