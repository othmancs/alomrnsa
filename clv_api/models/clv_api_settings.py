# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
   """
   To adds some settings to Cleverence API module
   """
   _inherit = 'res.config.settings'

   clv_default_scan_locations = fields.Boolean(string="Scan locations")
   clv_allow_only_lowest_level_locations = fields.Boolean(string="Only allow locations of the lowest level")
   clv_auto_create_backorders = fields.Boolean(string="Create backorder documents automatically")
   clv_use_fake_serials_in_receiving = fields.Boolean(string="Use fake serial numbers in receiving")
   clv_ship_expected_actual_lines = fields.Boolean(string="Show expected actual lines in SHIP document")

   def set_values(self):
      res = super(ResConfigSettings, self).set_values()
      config_params = self.env['ir.config_parameter'].sudo()
      config_params.set_param('clv_api.clv_default_scan_locations', self.clv_default_scan_locations)
      config_params.set_param('clv_api.clv_allow_only_lowest_level_locations', self.clv_allow_only_lowest_level_locations)
      config_params.set_param('clv_api.clv_auto_create_backorders', not self.clv_auto_create_backorders)
      config_params.set_param('clv_api.clv_use_fake_serials_in_receiving', self.clv_use_fake_serials_in_receiving)
      config_params.set_param('clv_api.clv_ship_expected_actual_lines', self.clv_ship_expected_actual_lines)
      return res

   def get_values(self):
      res = super(ResConfigSettings, self).get_values()
      config_params = self.env['ir.config_parameter'].sudo()
      value_scan_locations = config_params.get_param('clv_api.clv_default_scan_locations')
      value_only_lowest_locs = config_params.get_param('clv_api.clv_allow_only_lowest_level_locations')
      auto_backorders_value = not config_params.get_param('clv_api.clv_auto_create_backorders')
      use_fake_serials_value = config_params.get_param('clv_api.clv_use_fake_serials_in_receiving')
      ship_expected_actual_lines_value = config_params.get_param('clv_api.clv_ship_expected_actual_lines')
      res.update(
         clv_default_scan_locations=bool(value_scan_locations),
         clv_allow_only_lowest_level_locations=bool(value_only_lowest_locs),
         clv_auto_create_backorders=bool(auto_backorders_value),
         clv_use_fake_serials_in_receiving=bool(use_fake_serials_value),
         clv_ship_expected_actual_lines=bool(ship_expected_actual_lines_value)
      )
      return res

