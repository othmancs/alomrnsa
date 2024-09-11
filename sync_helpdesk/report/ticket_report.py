# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo import tools

AVAILABLE_PRIORITIES = [
   ('0', 'All'),
   ('1', 'Low Priority'),
   ('2', 'High Priority'),
   ('3', 'Urgent')
]

AVAILABLE_KANBAN_STATE = [
('normal', 'Normal'),
('blocked', 'Blocked'),
('done', 'Ready for next stage')
]


class TicketReport(models.Model):
    """ Ticket Report"""
    _name = "ticket.report"
    _auto = False
    _description = "Ticket Report"

    dont_email = fields.Boolean(string="Don't Email")
    work_approved = fields.Boolean(string='Approved work')
    name = fields.Char(string='Subject')
    partner_email = fields.Char(string='Customer Email')
    create_date = fields.Datetime(string='Created On')
    deadline = fields.Datetime(string='Deadline')
    write_date = fields.Datetime(string='Last Updated on')
    # message_last_post = fields.Datetime('Last Message Date')
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority', groups="sync_helpdesk.group_enable_ticket_priority")
    kanban_state = fields.Selection(AVAILABLE_KANBAN_STATE, string="Kanban State")
    user_id = fields.Many2one('res.users', string='Assigned to')
    company_id = fields.Many2one('res.company', string='Company')
    create_uid = fields.Many2one('res.users', string='Created By')
    partner_id = fields.Many2one('res.partner', string='Customer')
    team_id = fields.Many2one('ticket.team', string='Ticket Team')
    write_uid = fields.Many2one('res.users', string='Last Updated By')
    stage_id = fields.Many2one('ticket.stage', string='Stage')
    categ_id = fields.Many2one('ticket.category', string='Ticket Type')
    medium_id = fields.Many2one('utm.medium', string='Origin')

    def _select(self):
        """
            Create method for select ticket values
        """
        select_str = """
            SELECT
                    min(s.id) as id,
                    s.name,
                    s.user_id as user_id,
                    s.company_id as company_id,
                    s.partner_name,
                    s.create_uid,
                    s.write_uid,
                    -- s.message_last_post as message_last_post,
                    s.create_date as create_date,
                    s.write_date as write_date,
                    s.partner_id as partner_id,
                    s.partner_email as partner_email,
                    s.deadline as deadline,
                    s.team_id as team_id,
                    s.kanban_state as kanban_state,
                    s.priority as priority,
                    s.stage_id as stage_id,
                    s.categ_id as categ_id,
                    s.medium_id as medium_id,
                    s.dont_email as dont_email,
                    s.work_approved as work_approved,
                    s.date as date
        """
        return select_str

    def _from(self):
        """
            Create method for assign value table
        """
        from_str = """
            FROM
                ticket_ticket s
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY s.user_id,s.team_id,s.categ_id,s.stage_id,s.partner_id,s.partner_email,s.company_id,s.partner_name,s.create_uid,s.write_uid,
                s.name,s.create_date,s.write_date,s.priority,s.deadline,s.kanban_state,s.medium_id,s.dont_email,s.work_approved,s.date
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s as (
                %s %s %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
