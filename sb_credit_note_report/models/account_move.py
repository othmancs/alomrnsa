from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_method = fields.Selection([
        ('option1', 'نقدى'),
        ('option2', 'اجل'),
    ], string='طريقه الدفع', required=True)
    created_by_id = fields.Many2one('res.partner', string='انشأ من قبل', domain="[('branch_id', '=', branch_id)]")
    total_purchase_price = fields.Float(string="TOTAL", compute="_compute_total_price")

    @api.depends('invoice_line_ids.purchase_price')
    def _compute_total_price(self):
        for record in self:
            record.total_purchase_price = sum(rec.purchase_price for rec in record.invoice_line_ids)




class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    purchase_price = fields.Float(string="COST")


