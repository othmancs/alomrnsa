from odoo import models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def unlink(self):
        for rec in self:
            if rec.state == 'draft' and self.env.user.has_group('sb_group_access.no_delete_draft_picking'):
                raise UserError(_("لـيس لديـك صلاحيــة الحــذف"))
        return super(StockPicking, self).unlink()
