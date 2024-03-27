from odoo import api, fields, models


class ApprovalRequest(models.Model):
    _name = 'approval.request'
    _inherit = ['portal.mixin', 'approval.request']

    category_id = fields.Many2one(
        domain="[('custom_approval_type', '=', 'none')]",
    )
    attachment_ids = fields.One2many(
        comodel_name='ir.attachment',
        compute='_compute_attachment_ids',
        string="Main Attachments",
        help="Attachments that don't come from a message.")

    def _get_attachments_search_domain(self):
        self.ensure_one()
        return [('res_id', '=', self.id), ('res_model', '=', 'approval.request')]

    def _compute_attachment_ids(self):
        for record in self:
            attachment_ids = self.env['ir.attachment'].sudo().search(record._get_attachments_search_domain()).ids
            message_attachment_ids = record.mapped('message_ids.attachment_ids').ids  # from mail_thread
            record.attachment_ids = [(6, 0, list(set(attachment_ids) - set(message_attachment_ids)))]

    def _compute_access_url(self):
        super(ApprovalRequest, self)._compute_access_url()
        for record in self:
            record.access_url = f'/my/approval_requests/request/{record.id}'

    @api.model
    def create(self, values):
        result =super(ApprovalRequest, self).create(values)
        for record in result:
            record._portal_ensure_token()
        return result
