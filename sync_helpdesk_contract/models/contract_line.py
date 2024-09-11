# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _


# class ContractContractLine(models.Model):
#     _name = "contract.contract.line"
#     _description = 'Contract Line'

#     contract_id = fields.Many2one('contract.contract', string='Contract', help="contract", ondelete="cascade")
#     product_id = fields.Many2one('product.product', string='Product', required=True)
#     name = fields.Char(string='Description', size=256, required=True)
#     categ_id = fields.Many2one('product.category', string='Product Category', required=True)
#     analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
#                                           related='contract_id.analytic_account_id')
#     partner_id = fields.Many2one('res.partner', string='Customer', related='contract_id.partner_id', store=True)
#     date_start = fields.Datetime(string='Date Start', related='contract_id.date_start', readonly=True)
#     date_end = fields.Datetime(string='Date End', related='contract_id.date_end', readonly=True)
#     service_hours_from = fields.Float(string='Service Hours(From)', related='contract_id.service_hours_from', readonly=True)
#     service_hours_to = fields.Float(string='Service Hours(To)', related='contract_id.service_hours_to', readonly=True)
#     state = fields.Selection(related='contract_id.state', string='state', readonly=True, copy=False)
#     # state = fields.Selection(related='contract_id.state', selection=[('template', 'Template'), ('draft', 'New'),
#     #                                                                  ('open', 'Open'), ('pending', 'Pending'),
#     #                                                                  ('cancelled', 'Cancelled'), ('close', 'Closed')],
#     #                          string='state', readonly=True, copy=False)

#     @api.onchange('product_id')
#     def product_id_change(self):
#         """
#             Change related fields depending on product_id
#         """
#         self.name = self.product_id.name_get() and self.product_id.name_get()[0][1] if self.product_id else False
#         self.categ_id = self.product_id.categ_id.id if self.product_id and self.product_id.categ_id else False


class ContractServiceLine(models.Model):
    _name = 'contract.service.line'
    _description = "Contract Service Line"

    name = fields.Char(string='Description', size=256, required=True)
    contract_id = fields.Many2one('contract.contract', string="Contract")
    product_id = fields.Many2one('product.product', string='Service', required=True,
                                 domain=[('contract_ok', '=', True)])
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    used_qty = fields.Integer(string='Used Qty', compute='_service_analysis')
    remaining_qty = fields.Integer(string='Remaining Qty', compute='_service_analysis')

    @api.depends('contract_id', 'product_id')
    def _service_analysis(self):
        """ It will fetch service line product quantity """
        for obj in self:
            ticket_ids = self.env['ticket.ticket'].search([('contract_id', '=', obj.contract_id.id),
                                                           ('service_id', '=', obj.product_id.id)])
            if obj.product_uom_qty >= len(ticket_ids):
                obj.used_qty = len(ticket_ids)
                obj.remaining_qty = obj.product_uom_qty - len(ticket_ids)
            elif len(ticket_ids) == 0:
                obj.used_qty = len(ticket_ids)
                obj.remaining_qty = obj.product_uom_qty - len(ticket_ids)
            else:
                obj.used_qty = 0
                obj.remaining_qty = 0

    @api.onchange('product_id')
    def product_id_change(self):
        """
            Create method for set name depends on product name
        """
        self.product_uom = self.product_id.uom_id.id or False
        self.name = self.product_id.name or False
