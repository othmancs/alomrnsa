
# from odoo import models, fields, api

# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'

#     pricelist_item_id = fields.Many2one('product.pricelist.item', store=True)  # جعل الحقل مخزنًا
from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # إزالة الحقل غير المخزن وإنشاء حقل جديد مخزن
    pricelist_item_id = fields.Many2one('product.pricelist.item', store=True)  # جعل الحقل مخزنًا

    @api.model
    def _remove_old_field(self):
        # تنفيذ أوامر لإزالة الحقول القديمة من النموذج إذا لزم الأمر
        self.env.cr.execute('''ALTER TABLE sale_order_line DROP COLUMN IF EXISTS pricelist_item_id''')
