# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class HRContract(models.Model):
    _name = 'hr.contract'
    _inherit = ['mail.thread', 'hr.contract']

    signon_bonus = fields.Boolean('Sign on Bonus')
    signon_bonus_amount = fields.Float('Bonus Amount', digits=(16, 2), help="Mention the Sign on Bonus amount.")
    period_ids = fields.Many2many('year.period', string='Month(s)',
                                  help='Specify month(s) in which the sign on bonus will be distributed. '
                                       'Bonus will be distributed in Bonus Amount/Number of Month(s).')
    notice_start_date = fields.Date('Notice Start Date', readonly=True)
    notice_end_date = fields.Date('Notice End Date', readonly=True)
    is_leaving = fields.Boolean('Leaving Notice')
    basic = fields.Float('Basic', tracking=True, help='Basic Salary of Employee(value after gross/1.35)')
    HRA = fields.Float(string='House Rent Allowance', tracking=True, help="HRA of employee (25% of basic)") # , compute='_get_amount'
    TA = fields.Float(string='Transport Allowance', tracking=True,
                      help="Transport Allowance of employee (10% of Basic)")
    before_notification_day = fields.Integer('Before Notification Days (End Date)', default=60)
    early_notification_day = fields.Integer(string='Early Notification Days (End Date)', default=15)

    @api.constrains('wage')
    def check_wage(self):
        for rec in self:
            if rec.wage <= 0.0:
                raise UserError('Please define Wage must be greater than 0.0!')

    @api.onchange('wage')
    def _onchange_wage(self):
        if self.wage > 0:
            self.basic = self.wage / 1.35
            self.HRA = self.basic * 0.25
            self.TA = self.basic * 0.1

    @api.model
    def run_scheduler(self):
        """
            sent an email with notification of contract state, automatically sent an email to the client.
        """
        contract_ids = self.search([('state', 'in', ['draft', 'open'])])
        try:
            template_id = self.env.ref('saudi_hr_contract.email_template_hr_contract_notify')
        except ValueError:
            template_id = False
        hr_groups_config_obj = self.env['hr.groups.configuration']
        for contract in contract_ids:
            if contract.date_end:
                notify_date = contract.date_end - relativedelta(days=contract.before_notification_day)
                early_notification_date = contract.date_end - relativedelta(days=contract.early_notification_day)
                if fields.Date.today() == notify_date or fields.Date.today() == early_notification_date:
                    hr_groups_config_ids = hr_groups_config_obj.search([('branch_id', '=', contract.employee_id.branch_id.id or False), ('hr_ids', '!=', False)])
                    hr_groups_ids = hr_groups_config_ids and hr_groups_config_obj.browse(hr_groups_config_ids.ids)[0]
                    user_ids = hr_groups_ids and [item.user_id.id for item in hr_groups_ids.hr_ids if item.user_id] or []
                    if contract.hr_responsible_id:
                        user_ids.append(contract.hr_responsible_id.id)
                    email_to = ''
                    res_users_obj = self.env['res.users']
                    for user_id in res_users_obj.browse(user_ids):
                        if user_id.email:
                            email_to = email_to and email_to + ',' + user_id.email or email_to + user_id.email
                    if template_id:
                        template_id.write({'email_to': email_to, 'reply_to': email_to, 'auto_delete': False})
                        template_id.send_mail(contract.id, force_send=True)
        return True
