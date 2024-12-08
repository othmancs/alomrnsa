# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT


class hr_employee(models.Model):
    _inherit = 'hr.employee'


    leave_date = fields.Date(string="Leaving Date")