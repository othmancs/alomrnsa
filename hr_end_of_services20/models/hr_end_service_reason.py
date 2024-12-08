# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT

class hr_end_service_reason(models.Model):
    _name = 'hr.end.service.reason'


    name = fields.Char(string="Name", required=True)
    reason_type= fields.Selection([('termination','Termination'),('resign','Resignation'),('end','End of Contract')], required=True)