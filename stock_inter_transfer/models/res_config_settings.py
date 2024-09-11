# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    transfer_approval_required = fields.Boolean(string="Transfer Approval Required",
                                                help="Approval is needed to transfer stock from one WH to other.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['transfer_approval_required'] = self.env['ir.config_parameter'].sudo().get_param('transfer_approval_required', False)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("transfer_approval_required", self.transfer_approval_required or False)
