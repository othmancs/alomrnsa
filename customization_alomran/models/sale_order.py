from odoo import fields, models, api
import qrcode
import base64
import io


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qr_code_img = fields.Binary(string="QR Code Image", compute="compute_sh_qr_code_img", store=True)

    @api.depends('product_id')
    def compute_sh_qr_code_img(self):
        for rec in self:
            rec.qr_code_img = False

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            qr.add_data(rec.product_id.qr_code_url)
            qr.make(fit=True)

            img = qr.make_image()
            temp = io.BytesIO()
            img.save(temp, format="PNG")
            qr_code_image = base64.b64encode(temp.getvalue())
            rec.qr_code_img = qr_code_image

    # @api.onchange('product_id')
    # def _onchange_product_id_set_warehouse(self):
    #     for line in self:
    #         line.product_warehouse_id = line.product_id.categ_id.stock_warehouse_id.id
    @api.onchange('product_id')
    def _onchange_product_id_set_warehouse(self):
        for line in self:
            line.product_warehouse_id = line.product_id.categ_id.stock_warehouse_ids and line.product_id.categ_id.stock_warehouse_ids[0].id or False

