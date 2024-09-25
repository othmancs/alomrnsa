from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_name = fields.Char(string='اسم العميل')
    customer_phone = fields.Char(string='رقم الجوال')

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
        })
        return invoice_vals
    def name_search_customer_info(self, name='', args=None, operator='ilike', limit=100):
        if self._context.get('search_by_customer', False):
            if name:
                args = args if args else []
                args.extend(['|', ['customer_name', operator, name], ['customer_phone', operator, name]])
                name = ''
        return super(SaleOrder, self).name_search(name=name, args=args, operator=operator, limit=limit)
