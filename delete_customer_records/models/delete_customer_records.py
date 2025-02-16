from odoo import models, api


class DeleteCustomerRecords(models.Model):
    _name = 'delete.customer.records'
    _description = 'Delete All Customer Transactions'

    def action_delete_customer_data(self):
        # حذف جميع القيود المحاسبية المتعلقة بالعملاء
        self.env['account.move'].search([('partner_id', '!=', False)]).unlink()

        # حذف جميع المدفوعات المرتبطة بالعملاء
        self.env['account.payment'].search([('partner_id', '!=', False)]).unlink()

        # حذف جميع الفواتير المرتبطة بالعملاء
        self.env['account.move'].search([('move_type', 'in', ['out_invoice', 'out_refund'])]).unlink()

        # حذف جميع العملاء بعد حذف جميع حركاتهم
        self.env['res.partner'].search([('customer_rank', '>', 0)]).unlink()

        return {'type': 'ir.actions.client', 'tag': 'reload'}