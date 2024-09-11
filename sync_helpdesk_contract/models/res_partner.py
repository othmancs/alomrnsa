# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def total_count(self):
        """
            Compute total number of contracts
        """
        self.ensure_one()
        self.contract_count = self.env['contract.contract'].search_count([('partner_id', '=', self.id)])

    def current_contract_detail(self):
        """
            Show contract
        """
        contract_ids = self.env['contract.contract'].search([('partner_id', '=', self.id)])
        result = self.env['ir.actions.actions']._for_xml_id('sync_helpdesk_contract.support_contracts_action')
        result['views'] = [(self.env.ref('sync_helpdesk_contract.contract_contract_tree_view').id, 'tree'),
                           (self.env.ref('sync_helpdesk_contract.contract_contract_form_view').id, 'form')]
        result['domain'] = [('id', 'in', contract_ids.ids)]
        return result

    contract_count = fields.Integer(compute="total_count", string="Contract")
