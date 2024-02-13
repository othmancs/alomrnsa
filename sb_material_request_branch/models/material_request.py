from odoo import fields, models, api


class MaterialRequest(models.Model):
    _inherit = 'material.request'

    branch_from_id = fields.Many2one(
        'res.branch',
        string='فرع من',
        domain=lambda self: [('id', 'in', self.env.user.branch_ids.ids)],
        default=lambda self: self.env.user.branch_id.id,
    )
    branch_to_id = fields.Many2one(
        'res.branch',
        string='فرع الى',
        domain=lambda self: [('id', 'in', self.env.user.branch_ids.ids)],
        default=lambda self: self.env.user.branch_id.id,
    )

    @api.onchange('branch_from_id',)
    def _onchange_branch_from_id(self):
        """
        set domain in branch from
        """
        for rec in self:
            rec.location_id = False
            if rec.branch_from_id:
                related_locations = self.env['stock.location'].search([
                    ('branch_id', '=', rec.branch_from_id.id),
                    ('usage', '=', 'internal')]
                )
                return {'domain': {'location_id': [
                    ('id', 'in', related_locations.ids)
                ]}}
            return {'domain': {'location_id': [('id', '=', False)]}}

    @api.onchange('branch_to_id', )
    def _onchange_branch_to_id(self):
        """
        set domain in branch to
        """
        for rec in self:
            rec.dest_location_id = False
            if rec.branch_to_id:
                related_locations = self.env['stock.location'].search([
                    ('branch_id', '=', rec.branch_to_id.id),
                    ('usage', '=', 'internal')]
                )
                return {'domain': {'dest_location_id': [
                    ('id', 'in', related_locations.ids)
                ]}}
            return {'domain': {'dest_location_id': [('id', '=', False)]}}
