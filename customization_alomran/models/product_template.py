from odoo import fields, models, api
import qrcode
import base64
import io
import re


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    qr_code_url = fields.Char(string='QR Code Link')
    qr_code_img = fields.Binary(string="QR Code Image", compute="compute_sh_qr_code_img", store=True)

    @api.depends('qr_code_url')
    def compute_sh_qr_code_img(self):
        for rec in self:
            rec.qr_code_img = False

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            qr.add_data(rec.qr_code_url)
            qr.make(fit=True)

            img = qr.make_image()
            temp = io.BytesIO()
            img.save(temp, format="PNG")
            qr_code_image = base64.b64encode(temp.getvalue())
            rec.qr_code_img = qr_code_image

    # @api.model
    # def _name_search(self, name, args=None, operator='like', limit=100):
    #     domain = args or []
    #     if name:
    #         pattern = re.compile('^|','^|'.format(re.escape(name)), re.IGNORECASE)
    #         filtered_ids = [record.id for record in self.search(domain, limit=limit) if pattern.match(record.default_code)]
    #         print('filtered_ids',filtered_ids)
    #         domain = [('id', 'in', filtered_ids)]
    #     return super(ProductTemplate, self)._name_search( name=name,args=domain, operator=operator, limit=limit)
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        product_ids = []
        if self._context.get("partner_id") and not self._context.get('product_id'):
            partner_id = self.env["res.partner"].browse(self._context["partner_id"])
            product_ids = self.with_context(product_id=True).search([('partner_id', '=', partner_id)])
                return set(product_ids)
        return super()._search(args, offset, limit, order, count, access_rights_uid)
