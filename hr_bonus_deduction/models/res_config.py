# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    deduction_amount = fields.Float(string='Deduction Amount')
    bonus_amount = fields.Float(string='Bonus Amount')

    # @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()

        config_parameters = self.env['ir.config_parameter'].sudo()
        config_parameters.set_param('deduction_amount', self.deduction_amount)
        config_parameters.set_param('bonus_amount', self.bonus_amount)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        config_parameters = self.env['ir.config_parameter'].sudo()
        deduction_amount = config_parameters.get_param('deduction_amount')
        bonus_amount = config_parameters.get_param('bonus_amount')

        res.update(
            deduction_amount=float(deduction_amount),
            bonus_amount=float(bonus_amount)
        )
        return res
