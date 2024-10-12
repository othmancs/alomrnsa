from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    name_custom = fields.Char(string="اسم العميل")
    num_custom = fields.Char(string="رقم الجوال")

    # إعداد الفاتورة مع تمرير الحقول المخصصة
    @api.model
    def _prepare_invoice(self):
        # تأكد من أنك تستدعي super بشكل صحيح بدون self
        invoice_vals = super()._prepare_invoice()
        if self.name_custom and self.num_custom:
            invoice_vals.update({
                'name_custom': self.name_custom,
                'num_custom': self.num_custom,
            })
        return invoice_vals
    def get_account_move_views(self):
        views = self.env['ir.ui.view'].search([('model', '=', 'account.move')])
        view_names = views.name_get()
        return view_names

class AccountMove(models.Model):
    _inherit = 'account.move'

    # إضافة الحقول في نموذج الفاتورة
    name_custom = fields.Char(string="اسم العميل")
    num_custom = fields.Char(string="رقم الجوال")

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # توريث الحقول في شاشة التوصيل
    name_custom = fields.Char(string="اسم العميل")
    num_custom = fields.Char(string="رقم الجوال")

    @api.model
    def create(self, vals):
        if 'sale_id' in vals:
            sale_order = self.env['sale.order'].browse(vals['sale_id'])
            vals.update({
                'name_custom': sale_order.name_custom,
                'num_custom': sale_order.num_custom,
            })
        return super(StockPicking, self).create(vals)
