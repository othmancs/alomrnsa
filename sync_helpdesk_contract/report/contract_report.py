# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo import tools

periods = [('days', 'Day(s)'), ('weeks', 'Week(s)'), ('months', 'Month(s)'), ('years', 'Year(s)')]

states = [('draft', 'New'),
          ('confirm', 'Confirm'),
          ('progress', 'In Progress'),
          ('open', 'Open'),
          ('pending', 'Pending'),
          ('cancelled', 'Cancelled'),
          ('close', 'Closed'),
          ('invoiced', 'Invoiced')]


class TicketContractReport(models.Model):
    """ Ticket Report"""
    _name = "contract.report"
    _auto = False
    _description = "Contract Report"

    name = fields.Char(string='Analytic Account')
    code = fields.Char(string='Reference')
    response_hours = fields.Float(string='Response Time')
    date_start = fields.Datetime('Date Start')
    date_end = fields.Datetime('Date End')
    contract_period = fields.Selection(periods, string='Period')
    state = fields.Selection(states, string='State')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Account Name')
    user_id = fields.Many2one('res.users', 'Assigned to')
    parent_id = fields.Many2one('account.analytic.account', string='Parent Account')
    partner_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Service')
    contact_id = fields.Many2one('res.partner', string='Contact')

    def _select(self):
        select_str = """
            SELECT
                min(a.id) as id,
                a.user_id as user_id,
                a.date_start as date_start,
                a.date_end as date_end,
                a.product_id as product_id,
                a.analytic_account_id as analytic_account_id,
                a.state as state,
                a.contract_period as contract_period,
                o.parent_id as parent_id,
                o.partner_id as partner_id,
                o.code as code,
                o.name as name,
                a.contact_id as contact_id,
                a.response_hours as response_hours
        """
        return select_str

    def _from(self):
        from_str = """
            FROM
                contract_contract a
                JOIN account_analytic_account o on (a.analytic_account_id=o.id)
            """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY  a.user_id,a.date_start,a.date_end,a.product_id,a.analytic_account_id,a.contract_period,a.state,o.parent_id,o.partner_id,o.code,o.name,a.contact_id,a.response_hours
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s as (
                %s %s %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
