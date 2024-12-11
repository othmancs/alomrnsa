#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning


class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    foreign_name = fields.Char(string="Foreign Name", help="Foreign Name")


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    swift_code = fields.Char('Swift Code')

# FIXME THIS Model SHOULD BE REMOVED
class Employee(models.Model):
    _inherit = 'hr.employee'

    passport_expiry = fields.Date(string='تاريخ انتهاء الجواز')
    iqama_date = fields.Date(string='تاريخ اصدار الإقامة')
    on_kingdom = fields.Boolean(string='خارج المملكة')
    iqama_expiry_date = fields.Date(string='تاريخ انتهاء الإقامة ')
    iqama_expiry_date_hijri = fields.Char(string='تاريخ انتهاء الإقامة بالهجري')
    manager_phone = fields.Char(string='رقم صاحب العمل')

