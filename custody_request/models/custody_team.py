# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleTeam(models.Model):
    _name = "custody.team.custom"
    _description = "Custody Team"

    active = fields.Boolean('Active', default=True)

    name = fields.Char('Name')

    user_id = fields.Many2one(
        comodel_name='res.users', string='Team Leader',
        default=lambda self: self.env.user, required=True, index=True)

    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        required=True, index=True, default=lambda self: self.env.company.id)

    lock_amount_total = fields.Boolean(
        string="Lock Amount Total",
        help="Prevent changes of amount total if approval route generated"
    )

    approver_ids = fields.One2many('custody.team.approver','team_custom_id', string='Approvers')

    @api.constrains('company_id')
    def _check_team_company(self):
        for team in self:
            if team.company_id.custody_approval_route == 'no':
                raise UserError(_('Approval Route functionality is disabled for the company %s') % team.company_id.name)


class SaleTeamApprover(models.Model):
    _name = "custody.team.approver"
    _description = "CustodyTeam Approver"
    _order = 'sequence'
    _rec_name = 'sequence'

    sequence = fields.Integer(string='Sequence', default=10)

    team_custom_id = fields.Many2one('custody.team.custom', string='Team', ondelete='cascade')

    user_id = fields.Many2one(
        comodel_name='res.users', string='Approver',
        required=True)

    role = fields.Char('Role/Position', required=True, default="Approver")

    min_amount = fields.Monetary(
        string="Minimum Amount",
        currency_field='company_currency_id', readonly=False,
        help="""Minimum Amount (included) for which a validation by approver is required.
        If Total Amount is less than Minimum Amount then the approver will be skipped.""")

    max_amount = fields.Monetary(
        string="Maximum Amount",
        currency_field='company_currency_id', readonly=False,
        help="""Maximum Amount (included) for which a validation by approver is required. 
        If Total Amount is greater than Maximum Amount then the approver will be skipped.""")

    company_currency_id = fields.Many2one(
        comodel_name='res.currency', string="Company Currency",
        related='team_custom_id.company_id.currency_id', readonly=True,
        help='Utility field to express threshold currency')

    lock_amount_total = fields.Boolean(
        string="Lock Amount Total",
        help="Prevent changes of amount total if Custody approved by this user"
    )

    custom_condition_code = fields.Text(
        string='Custom Condition Code',
        help='You can enter python expression to define custom condition'
    )

    @api.onchange('user_id')
    def _detect_user_role(self):
        for approver in self:
            # if user related to employee, try to get job title for hr.employee
            employee = hasattr(approver.user_id, 'employee_ids') and getattr(approver.user_id, 'employee_ids')
            employee_job_id = hasattr(employee, 'job_id') and getattr(employee, 'job_id')
            employee_job_title = employee_job_id.name if employee_job_id else False
            if employee_job_title:
                approver.role = employee_job_title
                continue
            # if user related partner, try to get job title for res.partner
            partner = approver.user_id.partner_id
            partner_job_title = hasattr(partner, 'function') and getattr(partner, 'function')
            if partner_job_title:
                approver.role = partner_job_title


class CustodyApprover(models.Model):
    _name = "custody.order.approver"
    _inherit = "custody.team.approver"
    _description = "Custody Approver"
    _order = 'state asc'

    team_approver_id = fields.Many2one(
        comodel_name='custody.team.approver', string='Custody Team Approver',
        ondelete='set null')

    order_id = fields.Many2one(
        comodel_name='custody.request', string='Order',
        required=True, ondelete='cascade')

    state = fields.Selection(
        selection=[
            ('to approve', 'To Approve'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ], string='Status', readonly=True, required=True, default='to approve')