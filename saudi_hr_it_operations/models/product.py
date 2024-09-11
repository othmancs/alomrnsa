# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields
import qrcode
import qrcode.image.svg
import base64
from io import BytesIO


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    qr_code = fields.Char("QR Code", copy=False, compute='generate_qr_code')
    qr_code_image = fields.Binary(string='qr code image', store=True)
    is_equipment = fields.Boolean(string='Is Equipment', default=False)
    equipment_company_id = fields.Many2one('res.company', string='Equipment Company')
    
    def generate_qr_code(self):
        def get_qr_encoding(tag, field):
            value = field.encode('UTF-8')
            tag = tag.to_bytes(length=1, byteorder='big')
            length = len(value).to_bytes(length=1, byteorder='big')
            return tag + length + value

        for rec in self:
            qr_code_str = ''
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            action = self.env.ref('stock.product_template_action_product')
            menu_id = self.env.ref('stock.menu_product_variant_config_stock')
            url = base_url + '/web#id=' + str(rec.id) + '&menu_id=' + str(menu_id.id) + '&action=' + str(action.id) + '&model=product.template&view_type=form'
            str_to_encode = get_qr_encoding(1, url)
            qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
            rec.qr_code = qr_code_str
            img = qrcode.make(url, image_factory=qrcode.image.svg.SvgImage)
            temp = BytesIO()
            img.save(temp)
            qr_img = base64.b64encode(temp.getvalue())
            rec.qr_code_image = qr_img

    def print_qr_label_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Print QR Label',
            'res_model': 'print.qr.label',
            'context': {'default_product_ids':[(6, 0, self.ids)]},
            'view_mode': 'form',
            'target': 'new'
        }
