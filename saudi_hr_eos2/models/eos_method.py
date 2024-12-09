
from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class EOSMethod(models.Model):
    _name = "eos.method"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    name=fields.Char(required=True,tracking=1)
    user_id = fields.Many2one('res.users', string='User Created', index=True, tracking=True,
                              default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company',readonly=True,default=lambda self: self.env.company)
    ticket_account_id = fields.Many2one('account.account',tracking=1)
    loan_account_id = fields.Many2one('account.account',tracking=1)
    other_deduction_account_id = fields.Many2one('account.account',tracking=1)
    other_allowance_account_id = fields.Many2one('account.account',tracking=1)
    remaining_leave_account_id = fields.Many2one('account.account',tracking=1)
