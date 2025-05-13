from odoo import models, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.ondelete(at_uninstall=False)
    def _check_partner_deletion(self):
        account_move_line = self.env['account.move.line']
        for partner in self:
            # التحقق من أن الشريك غير مؤرشف إذا كان لديه حركات محاسبية
            move_lines = account_move_line.search([('partner_id', '=', partner.id)], limit=1)
            if move_lines and partner.active:
                raise UserError(_(
                    "لا يمكن حذف الشريك النشط لأنه مستخدَم في المحاسبة.\n"
                    "يمكنك أرشفة الشريك أولاً ثم محاولة الحذف مرة أخرى."
                ))

    def unlink(self):
        # التحقق الإضافي قبل الحذف
        for partner in self:
            if partner.user_ids:
                raise UserError(_(
                    "لا يمكن حذف الشريك لأنه مرتبط بمستخدمين.\n"
                    "الرجاء إلغاء ارتباط المستخدمين أولاً."
                ))
        return super().unlink()