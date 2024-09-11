# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    transfer_id = fields.Many2one('stock.transfer', string="Transfer")

    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        for pick in self:
            if pick.transfer_id:
                picking_ids = pick.transfer_id.picking_ids.filtered(lambda l: l.state in ['draft', 'waiting', 'confirm'] and l.id != pick.id)
                if picking_ids:
                    for picking_id in picking_ids:
                        picking_id.action_assign()
        return res


class StockLocation(models.Model):
    _inherit = "stock.location"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = args or []
        context = dict(self.env.context or {})
        if context.get('check_source_location'):
            picking_type_id = self.env['stock.picking.type'].browse(context['check_source_location'])
            args.append(('id', 'in', self.search([]).filtered(lambda l: l.warehouse_id and l.warehouse_id.id == picking_type_id.warehouse_id.id).ids))
        return super(StockLocation, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
