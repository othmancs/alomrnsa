from odoo import fields, models, api, _


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    custom_approval_type = fields.Selection(
        string='Approval Category',
        selection=[('none', 'None')],
        default='none',
        required=False,
    )
    my_request_count = fields.Integer(
        compute='_compute_my_request_count',
    )

    def _compute_my_request_count(self):
        """
        get number of request
        """
        for record in self:
            record.my_request_count = 0
            if record.custom_approval_type == 'none':
                record.my_request_count = self.env['approval.request'].search_count([
                    ('request_owner_id', '=', self.env.user.id),
                    ('category_id', '=', record.id)
                ])


    def action_custom_show_requests(self):
        self.ensure_one()

        action_ref = self.env.ref(
            'approvals.approval_request_action_to_review_category')
        return {
            "type": action_ref.type,
            "name": action_ref.name,
            "res_model": action_ref.res_model,
            "views": action_ref.views or [(False, "tree"), (False, "form")],
            "domain": action_ref.domain or [],
            "context": action_ref.context or {},
            "help": action_ref.help or "No content available.",
        }

