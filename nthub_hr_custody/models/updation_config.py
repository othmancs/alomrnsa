# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class JournalConfig(models.TransientModel):
    _inherit = ['res.config.settings']

    # notice_period = fields.Boolean(string='Notice Period')
    # no_of_days = fields.Integer()
    stock_operation_type = fields.Many2one('stock.picking.type')
    it_operation_type = fields.Many2one('stock.picking.type')
    stock_source_location = fields.Many2one('stock.location')
    it_source_location = fields.Many2one('stock.location')
    destination_location = fields.Many2one('stock.location')
    portal_allow_api_keys = fields.Char()
    # statement = fields.Many2one('account.bank.statement')

    def set_values(self):
        super(JournalConfig, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        # param.set_param("hr_resignation.notice_period", self.notice_period)
        param.set_param('nthub_hr_custody.stock_operation_type', self.stock_operation_type.id)
        param.set_param('nthub_hr_custody.it_operation_type', self.it_operation_type.id)
        # param.set_param("hr_resignation.no_of_days", self.no_of_days)
        param.set_param("nthub_hr_custody.stock_source_location", self.stock_source_location.id)
        param.set_param("nthub_hr_custody.it_source_location", self.it_source_location.id)
        param.set_param("nthub_hr_custody.destination_location", self.destination_location.id)
        # param.set_param("hr_resignation.statement", self.statement.id)


    @api.model
    def get_values(self):
        res = super(JournalConfig, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['stock_operation_type'] = int(get_param('nthub_hr_custody.stock_operation_type'))
        res['it_operation_type'] = int(get_param('nthub_hr_custody.it_operation_type'))
        res['stock_source_location'] = int(get_param('nthub_hr_custody.stock_source_location'))
        res['it_source_location'] = int(get_param('nthub_hr_custody.it_source_location'))
        res['destination_location'] = int(get_param('nthub_hr_custody.destination_location'))
        return res
