from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseReport(models.Model):
    _name = 'purchase.report'
    _description = 'Purchase Report'

    name = fields.Char('Name')

    # Main Fields
    company_id = fields.Many2one('res.company', string="Company")
    date_order = fields.Datetime('Datetime')
    partner_id = fields.Many2one('res.partner', string="Vendor")
    product_id = fields.Many2one('product.product', string="Product")
    qty = fields.Float(string="Quantity")
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    price_unit = fields.Float(string="Unit Price")
    price_tax = fields.Float(string="Tax Amount")
    tax_id = fields.Many2many('account.tax', string="Taxes")
    subtotal = fields.Float(string="Subtotal")
    total = fields.Float(string="Total")

    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")
    
    # إذا كان `branch_id` مطلوبًا، أضفه هنا
    branch_id = fields.Many2one('res.branch', string="Branch")

    def fetch_purchase_data(self):
        """جلب بيانات الطلبات المؤكدة وتحديث التقرير"""
        self.ensure_one()  # يضمن استدعاء الوظيفة لسجل واحد فقط

        # حذف السجلات السابقة مع تجنب مشاكل الصلاحيات
        reports = self.env['purchase.report'].sudo().search([])
        if reports:
            reports.unlink()

        # جلب بيانات الطلبات المؤكدة
        purchase_order_lines = self.env['purchase.order.line'].search([('state', '=', 'purchase')])
        
        for line in purchase_order_lines:
            self.env['purchase.report'].create({
                'company_id': line.company_id.id,
                'name': line.order_id.name,
                'date_order': line.order_id.date_order,
                'partner_id': line.order_id.partner_id.id,
                'product_id': line.product_id.id,
                'qty': line.product_qty,
                'uom_id': line.product_uom.id,
                'price_unit': line.price_unit,
                'price_tax': line.price_tax,
                'tax_id': line.taxes_id.ids,
                'subtotal': line.price_subtotal,
                'total': line.price_total,
                'purchase_order_id': line.order_id.id,
                'branch_id': line.order_id.branch_id.id if hasattr(line.order_id, 'branch_id') else False,  # تجنب الخطأ في حالة عدم وجود `branch_id`
            })

    def action_refresh_report(self):
        """زر في الواجهة لتحديث التقرير يدويًا"""
        self.fetch_purchase_data()

