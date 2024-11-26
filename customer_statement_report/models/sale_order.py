from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_statement_data(self):
        """إرجاع بيانات كشف الحساب"""
        statement_lines = []
        for line in self.order_line:
            statement_lines.append({
                'date': line.create_date.strftime('%Y-%m-%d'),
                'description': line.product_id.name,
                'reference': line.name or '',
                'balance': line.price_total,
            })
        return statement_lines

    def _get_report_base_filename(self):
        """لتحديد اسم ملف PDF المصدّر"""
        return f"كشف حساب - {self.partner_id.name}"
