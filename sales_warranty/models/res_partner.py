# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    def count_warranty(self):
        for rec in self:
            rec.warranty_count = len(rec.warranty_ids) if rec.warranty_ids else 0

    warranty_count = fields.Integer(string="# Warranty", compute='count_warranty')
    warranty_ids = fields.One2many('warranty.detail', 'partner_id', string="Warranty")

    def action_view_warranty(self):
        """
            Show warranty records
        """
        if self.warranty_ids:
            action = self.env["ir.actions.actions"]._for_xml_id("sales_warranty.warranty_detail_action_all")
            if len(self.warranty_ids) > 1:
                action['domain'] = [('id', 'in', self.warranty_ids.ids)]
            elif len(self.warranty_ids) == 1:
                action['views'] = [(self.env.ref('sales_warranty.warranty_detail_form_view').id, 'form')]
                action['res_id'] = self.warranty_ids.ids[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action
