from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_type = fields.Selection([
        ('cash', 'كاش'),
        ('credit', 'آجل')
    ], string='نوع الدفع', tracking=True)  # إضافة tracking لتحديثات السجل

    # يمكنك التأكد من أن القيم الافتراضية للحقل صحيحة
    def _default_payment_type(self):
        return 'cash'  # إذا كان الحقل يجب أن يكون له قيمة افتراضية

    payment_type = fields.Selection([
        ('cash', 'كاش'),
        ('credit', 'آجل')
    ], string='نوع الدفع', default=_default_payment_type)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    purchase_price = fields.Float(string="التكلفة")



# from odoo import fields, models


# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     # payment_method = fields.Selection([
#     #     ('option1', 'نقدى'),
#     #     ('option2', 'اجل'),
#     # ], string='طريقه الدفع' ,readonly=True)
#     payment_type = fields.Selection([
#         ('cash', 'Cash'),
#         ('credit', 'Credit')
#     ], string='Payment Type')
#     # created_by_id = fields.Many2one('res.partner', string='انشأ من قبل', domain="[('branch_id', '=', branch_id)]",readonly=True)

# class AccountInvoiceLine(models.Model):
#     _inherit = 'account.move.line'

#     purchase_price = fields.Float(string="COST")
