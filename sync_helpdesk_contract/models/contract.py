# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning, UserError
from odoo import models, fields, api, _


periods = [('days', 'Day(s)'), ('weeks', 'Week(s)'), ('months', 'Month(s)'), ('years', 'Year(s)')]


class ContractContract(models.Model):
    _name = "contract.contract"
    _inherit = ['mail.thread']
    _inherits = {'account.analytic.account': "analytic_account_id"}
    _description = "Contract"

    @api.depends('date_start', 'date_end')
    def _get_duration(self):
        ''' Returns duration between start and end date '''
        for obj in self:
            obj.duration_in_days = self._get_duration_in_days(obj.date_start, obj.date_end)

    def _ticket_count(self):
        '''Return lenth of contract ticket '''
        for contract in self:
            contract.ticket_count = self.env['ticket.ticket'].search_count([('contract_id', '=', contract.id)])

    def _contract_count(self):
        '''Return lenth of same partner contract '''
        for contract in self:
            contract.contract_count = 0
            if contract.partner_id:
                contract.contract_count = self.search_count([('partner_id', '=', contract.partner_id.id), ('id', '!=', contract.id)])

    has_special_notes = fields.Boolean(string='Special Notes')
    twenty4_7_hours = fields.Boolean(string='24/7')
    code = fields.Char(string='Reference', index=True, tracking=True, default='New', copy=False)
    date_confirm = fields.Date(string='Confirmation Date', readonly=True, index=True,
                               help="Date on which contract is confirmed.")
    description = fields.Text('Description')
    special_notes = fields.Text(string='special_notes')
    contract_length = fields.Integer(string='Length', default=1)
    duration_in_days = fields.Integer(string='Duration (In Days)', compute='_get_duration')
    contract_count = fields.Integer(string='#Contract', compute='_contract_count')
    ticket_count = fields.Integer(string='#Ticket', compute='_ticket_count')
    service_hours_from = fields.Float(string='From')
    service_hours_to = fields.Float(string='To')
    response_hours = fields.Float(string='Response Time')
    date_start = fields.Datetime('Date Start', default=fields.Datetime.today(), required=True)
    date_end = fields.Datetime('Date End')
    contract_period = fields.Selection(periods, string='Period', default='months', tracking=True)
    state = fields.Selection([('template', 'Template'),
                              ('draft', 'New'),
                              ('confirm', 'Confirm'),
                              ('progress', 'In Progress'),
                              ('open', 'Open'),
                              ('pending', 'Pending'),
                              ('cancelled', 'Cancelled'),
                              ('close', 'Closed'),
                              ('invoiced', 'Invoiced')], 'State',
                             help=""" When an account is created its in \'Draft\' state.\
                             \n* If invoice is going to be created or any pending balance is there, it can be in \'Pending\'. \
                             \n* If invoice has been created, it can be in \'Invoiced\'. \
                             \n* If contract amount is paid or any associated partner is there, it can be in \'Open\' state.\
                             \n* If contract expired or when all the transactions are over, it can be in \'Close\' state. \
                             \n* If contract is cancelled, it can be in \'Cancel\' state. \
                             \n If it is to be reviewed then the state is \'Pending\'.\n When the contract is completed the state is set to \'Done\'.""",
                             default='draft', copy=False, tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Account Name', ondelete="cascade",
                                          required=True, index=True, help="Link contract to an analytic account. "
                                                                          "It enables you to connect contracts with "
                                                                          "budgets, planning, cost and revenue analysis,"
                                                                          " timesheets on contracts, etc.")
    contact_id = fields.Many2one('res.partner', string='Contact', tracking=True)
    user_id = fields.Many2one('res.users', 'Assigned to', default=lambda self: self.env.uid, tracking=True)
    product_id = fields.Many2one('product.product', string='Service', domain=[('contract_ok', '=', True)], required=True)
    service_line_ids = fields.One2many('contract.service.line', 'contract_id', string="Service line")

    @api.constrains('service_hours_from', 'service_hours_to', 'twenty4_7_hours')
    def _check_diff(self):
        if not self.twenty4_7_hours and self.service_hours_from == self.service_hours_to:
            raise UserError(_('Service hours, from and to must be different.'))

    @api.model
    def create(self, values):
        """ Override create method for update contract line values """
        service_line_ids = []
        if values.get('product_id'):
            product_id = self.env['product.product'].browse(values['product_id'])
            for service_line in product_id.service_line_ids:
                service_line_ids.append((0, 0, {
                    'name': service_line.name,
                    'product_uom_qty': service_line.product_uom_qty,
                    'product_uom': service_line.product_uom.id,
                    'product_id': service_line.product_id.id,
                }))
            # self.service_line_ids.unlink()
            values.update({'service_line_ids': service_line_ids})
        return super(ContractContract, self).create(values)

    def write(self, values):
        """ Override write method for update contract line values """
        service_line_ids = []
        for rec in self:
            if values.get('product_id'):
                product_id = self.env['product.product'].browse(values['product_id'])
                for service_line in product_id.service_line_ids:
                    service_line_data = {'name': service_line.name,
                                         'product_uom_qty': service_line.product_uom_qty,
                                         'product_uom': service_line.product_uom.id,
                                         'product_id': service_line.product_id.id,
                                         }
                    service_line_id = self.env['contract.service.line'].create(service_line_data)
                    service_line_ids.append(service_line_id.id)
                # rec.service_line_ids.unlink()
                values.update({'service_line_ids': [(6, 0, service_line_ids)]})
        return super(ContractContract, self).write(values)

    def unlink(self):
        """
            Override method for check delete validation
        """
        for objects in self:
            if objects.state not in ['draft']:
                raise Warning(_('You cannot remove the record(s) which is in this state!'))
        return super(ContractContract, self).unlink()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
            Create method for set contract id
        """
        if self.partner_id:
            contact_id = self.partner_id.child_ids.filtered(lambda l: l.type == 'contact')
            self.contact_id = contact_id[0].id if contact_id else self.partner_id.id

    def partner_contract_count(self):
        """
            Show Same partner Count Ticket.
        """
        self.ensure_one()
        count_contracts = self.search([('partner_id', '=', self.partner_id.id), ('id', '!=', self.id)])
        form_view = self.env.ref('sync_helpdesk_contract.contract_contract_form_view')
        tree_view = self.env.ref('sync_helpdesk_contract.contract_contract_tree_view')
        return {
            'name': 'Contract Number',
            'view_mode': 'form',
            'res_model': 'contract.contract',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', 'in', count_contracts.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True
        }

    def contract_ticket_count(self):
        """
            Show Same partner Count Ticket.
        """
        self.ensure_one()
        count_tickets = self.env['ticket.ticket'].search([('contract_id', '=', self.id)])
        form_view = self.env.ref('sync_helpdesk.support_ticket_view_form')
        tree_view = self.env.ref('sync_helpdesk.support_ticket_view_tree')
        return {
            'name': 'Ticket',
            'view_mode': 'form',
            'res_model': 'ticket.ticket',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', 'in', count_tickets.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True
        }

    def _get_duration_in_days(self, date_start, date_end):
        """ Returns duration of days or returns false """
        if date_start and date_end:
            return (date_end - date_start).days + 1
        return False

    def _get_date_end(self, length, period, date_start=False):
        """ Returns end date related the duration """
        context = self._context
        date_start = date_start or fields.Datetime.now()
        relative_date = relativedelta(days=length)
        if period == 'days':
            relative_date = relativedelta(days=length) - relativedelta(days=1)
        elif period == 'weeks':
            relative_date = relativedelta(weeks=length, days=-1)
        elif period == 'months':
            relative_date = relativedelta(months=length, days=-1)
        elif period == 'years':
            relative_date = relativedelta(years=length, days=-1)
        if context.get('contract_renew', False):
            return date_start + relative_date
        else:
            return date_start + relative_date

    def _get_date_start(self, length, period, date_end):
        """ Returns start date """
        relative_date = relativedelta(days=length)
        if period == 'days':
            relative_date = relativedelta(days=length) - relativedelta(days=1)
        else:
            if period == 'weeks':
                relative_date = relativedelta(weeks=length, days=-1)
            elif period == 'months':
                relative_date = relativedelta(months=length, days=-1)
            elif period == 'years':
                relative_date = relativedelta(years=length, days=-1)
        return date_end - relative_date

    def _get_dates(self, length, period, date_start=False, date_end=False):
        """
            Return end date or start date depending on contract length and period condition.
        """
        if length and period:
            if date_start:
                return date_start, self._get_date_end(length, period, date_start)
            elif date_end:
                return self._get_date_start(length, period, date_end), date_end
            else:
                return fields.Datetime.now(), self._get_date_end(length, period, date_start)
        return False, False

    @api.onchange('contract_period', 'contract_length', 'date_start')
    def contract_period_change(self):
        """ Contract period change related to time duration """
        if not self.contract_period:
            self.contract_length = False
        elif self.contract_length:
            date_start, date_end = self._get_dates(self.contract_length, self.contract_period, self.date_start, self.date_end)
            self.date_start = date_start
            self.date_end = date_end

        if self.contract_length and self.contract_period:
            self.date_start, self.date_end = self._get_dates(self.contract_length, self.contract_period, self.date_start, self.date_end)
        self.duration_in_days = self._get_duration_in_days(self.date_start, self.date_end)

    @api.onchange('date_end')
    def date_change(self):
        """ Change date related to duration """
        if self.date_end:
            date_start = self._get_date_start(self.contract_length, self.contract_period, self.date_end)
            self.date_start = date_start
        elif self.date_start:
            date_end = self._get_date_end(self.contract_length, self.contract_period, self.date_start)
            self.date_end = date_end
        else:
            date_start = fields.Datetime.now()
            date_end = self._get_date_end(self.contract_length, self.contract_period, self.date_start)
            self.date_start = date_start
            self.date_end = date_end
        self.duration_in_days = self._get_duration_in_days(self.date_start, self.date_end)

    @api.onchange('product_id')
    def product_id_change(self):
        """ Changes related fields on product_id """
        service_line_ids = []
        date_start = self.date_start or fields.Datetime.now()
        if self.product_id:
            self.service_line_ids = False
            date_end = self._get_date_end(self.product_id.contract_length, self.product_id.contract_period, date_start)
            for service_line in self.product_id.service_line_ids:
                service_line_ids.append((0, 0, {
                    'name': service_line.name,
                    'product_uom_qty': service_line.product_uom_qty,
                    'product_uom': service_line.product_uom.id,
                    'product_id': service_line.product_id.id,
                }))
            self.contract_length = self.product_id.contract_length
            self.contract_period = self.product_id.contract_period
            self.twenty4_7_hours = self.product_id.twenty4_7_hours
            self.service_hours_from = self.product_id.service_hours_from or 0.0
            self.service_hours_to = self.product_id.service_hours_to or 0.0
            self.response_hours = self.product_id.response_hours
            self.date_start = date_start
            self.date_end = date_end
            self.duration_in_days = self._get_duration_in_days(date_start, date_end)
            self.service_line_ids = service_line_ids

    def confirm_state(self):
        """
            Create method for confirm contract and send mail
        """
        self.ensure_one()
        if self.code == 'New':
            self.code = self.env['ir.sequence'].next_by_code('contract.contract')
        self.state = 'progress'
        self.date_confirm = fields.date.today()
        message = _("The contract '%s' has been confirmed.") % self.name
        self.message_post(subject=(_("Contract Confirmed")), body=message, message_type="comment")

    def action_close(self):
        """
            Set to close contract
        """
        for rec in self:
            rec.state = 'close'

    def action_cancel(self):
        """
            Set to cancel contract
        """
        for rec in self:
            rec.state = 'cancelled'

    def action_cancel_draft(self):
        """
            Set to draft contract
        """
        self.ensure_one()
        self.state = 'draft'
        message = _("The contract '%s' has been set in draft state.") % self.name
        self.message_post(subject=(_("Contract Reset")), body=message, message_type="comment")

    def set_pending(self):
        """
            Set to pending contract
        """
        for rec in self:
            rec.state = 'pending'

    def set_open(self):
        """
            Set to open contract
        """
        for rec in self:
            rec.state = 'open'

    def set_contract_open(self):
        """
            Set to open contract
        """
        for rec in self:
            rec.state = 'open'

    @api.model
    def scheduler_check_enddate(self):
        ''' It will check contract end date'''
        for data in self.search([('state', '=', 'open')]):
            if data.date_end:
                diff = fields.Datetime.now() - data.date_end
                if diff and abs(diff).days == 0:
                    data.state = 'close'
