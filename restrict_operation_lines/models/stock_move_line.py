from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    can_add_operation_lines = fields.Boolean(
        compute='_compute_can_add_operation_lines',
        string="Can Add Operation Lines",
        help="Indicates whether the user has permission to add operation lines."
    )

    @api.depends_context('uid')  # يتم تقييمه بناءً على سياق المستخدم
    def _compute_can_add_operation_lines(self):
        for record in self:
            # تحقق من وجود المستخدم في المجموعة
            record.can_add_operation_lines = self.env.user.has_group(
                'restrict_operation_lines.group_restrict_add_operation_lines'
            )
