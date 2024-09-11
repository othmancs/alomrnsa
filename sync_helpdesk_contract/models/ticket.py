# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Ticket(models.Model):
    _inherit = 'ticket.ticket'
    _description = 'Ticket'

    contract_id = fields.Many2one('contract.contract', string="Contract", domain=[('state', '=', 'open')], tracking=True)
    service_id = fields.Many2one('product.product', string="Service", tracking=True)

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        """ Change fields depending on contract_id """
        self.service_id = False

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
            Set contract value depends on partner
        """
        res = super(Ticket, self).onchange_partner_id()
        self.service_id = False
        contract_id = self.env['contract.contract'].search([('partner_id', '=', self.partner_id.id), ('state', '=', 'open')], limit=1)
        self.contract_id = contract_id.id if contract_id else False
        return res

    @api.model
    def create(self, vals):
        """
            Override create method for update service line values
        """
        if vals.get('partner_id') and vals.get('contract_id') and vals.get('service_id'):
            contract_id = self.env['contract.contract'].browse(vals['contract_id'])
            if contract_id and contract_id.service_line_ids:  # and not partner_id.support_without_payment:
                for line in contract_id.service_line_ids:
                    line._service_analysis()
                    if vals['service_id'] == line.product_id.id and line.product_uom_qty <= line.used_qty:
                        raise UserError("Your contract service remaining quantity is 0, Please update service product in contract.")
        return super(Ticket, self).create(vals)

    def write(self, vals):
        """
            Override write method for update service line values
        """
        for rec in self:
            if vals.get('contract_id') and vals.get('service_id'):
                contract_id = self.env['contract.contract'].browse(vals.get('contract_id'))
                for line in contract_id.service_line_ids:
                    line._service_analysis()
                    if vals['service_id'] == line.product_id.id and line.product_uom_qty <= line.used_qty:
                        raise UserError("Your contract service remaining quantity is 0, Please update service product in contract.")
        return super(Ticket, self).write(vals)
