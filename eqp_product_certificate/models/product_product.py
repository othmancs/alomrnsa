# -*- coding: utf-8 -*-

from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.product'

    certificate_ids = fields.One2many('product.certificate', 'product_id', string='product Certificates')
    product_certificate_count = fields.Integer(string='Product Certificate Count',
                                               compute='_compute_product_certificate_count')

    def action_view_certificates(self):
        action = self.env["ir.actions.actions"]._for_xml_id("eqp_product_certificate.action_product_certificate")
        action['domain'] = [('product_id', 'in', self.ids)]
        action['views'] = [(False, 'tree'), (False, 'form')]
        action['context'] = {
            'active_id': self._context.get('active_id'),
            'active_model': 'product.certificate',
        }
        return action

    def _compute_product_certificate_count(self):
        for product in self:
            product.product_certificate_count = product.env['product.certificate'].search_count([
                ('product_id', '=', product.id),
                ('active', '=', True),
            ])
