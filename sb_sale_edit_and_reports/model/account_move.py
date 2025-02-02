from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # payment_method = fields.Selection([
    #     ('option1', 'نقدى'),
    #     ('option2', 'اجل'),
    # ], string='طريقه الدفع' ,readonly=True)
    payment_type = fields.Selection([  # تم تغيير الحقل إلى Selection
        ('cash', 'نقدى'),
        ('credit', 'اجل'),
    ], string='Payment Type', required=True)
    created_by_id = fields.Many2one('res.partner', string='انشأ من قبل', domain="[('branch_id', '=', branch_id)]",readonly=True)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    purchase_price = fields.Float(string="COST")
