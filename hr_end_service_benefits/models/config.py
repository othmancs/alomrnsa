# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions
import math
import logging

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    settlement_journal_id = fields.Many2one(comodel_name="account.journal", string="Default Payment Journal", )
    expense_journal_id = fields.Many2one(comodel_name="account.journal", string="Default Expense Journal", )
    expense_account_id = fields.Many2one(comodel_name="account.account", string="Expense Account", )
    category_id = fields.Many2one(comodel_name="hr.salary.rule.category", string="Salary Net Category",
                                  required=False, )
    number_of_hours_per_day = fields.Float(default=8)


class config(models.TransientModel):
    _name = 'res.config.settings'
    _inherit = 'res.config.settings'

    settlement_journal_id = fields.Many2one(comodel_name="account.journal", related="company_id.settlement_journal_id",
                                            readonly=False)
    expense_journal_id = fields.Many2one(comodel_name="account.journal", related="company_id.expense_journal_id",
                                         readonly=False)
    expense_account_id = fields.Many2one(comodel_name="account.account", related="company_id.expense_account_id",
                                         readonly=False)
    category_id = fields.Many2one(comodel_name="hr.salary.rule.category", related="company_id.category_id",
                                  readonly=False)
    number_of_hours_per_day = fields.Float(related='company_id.number_of_hours_per_day', readonly=False)
