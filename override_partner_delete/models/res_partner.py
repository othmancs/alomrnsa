from odoo import models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def unlink(self):
        for partner in self:
            # إزالة القيود المرتبطة بالشريك قبل الحذف
            self.env.cr.execute("DELETE FROM account_move WHERE partner_id = %s", (partner.id,))
            self.env.cr.execute("DELETE FROM account_move_line WHERE partner_id = %s", (partner.id,))
            self.env.cr.execute("DELETE FROM account_invoice WHERE partner_id = %s", (partner.id,))
            self.env.cr.execute("DELETE FROM account_payment WHERE partner_id = %s", (partner.id,))
        return super(ResPartner, self).unlink()
