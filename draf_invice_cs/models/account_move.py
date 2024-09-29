# from odoo import models, api
# from odoo.exceptions import UserError

# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     def action_reset_to_draft(self):
#         for move in self:
#             # تحقق من أن الفاتورة في حالة منشورة
#             if move.state != 'posted':
#                 raise UserError('Only posted invoices can be reset to draft.')
#             # تغيير الحالة إلى "مسودة"
#             move.write({'state': 'draft'})
#             # إلغاء ترحيل القيود المحاسبية المرتبطة بالفاتورة
#             move.line_ids.remove_move_reconcile()
from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_reset_to_draft(self):
        for invoice in self:
            if invoice.state == 'posted':
                invoice.button_draft()
