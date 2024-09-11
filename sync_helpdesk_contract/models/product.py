# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _

periods = [('days', 'Day(s)'), ('weeks', 'Week(s)'), ('months', 'Month(s)'), ('years', 'Year(s)')]


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = 'Product Template'

    contract_ok = fields.Boolean(string="Can be Contracted")


class ProductProduct(models.Model):
    _inherit = "product.product"
    _description = 'Product Product'

    service_types = fields.Selection([('contract', 'Contract')], string='Service Type', default='')
    contract_length = fields.Integer(string='Length', required=True, default=1.0)
    contract_period = fields.Selection(periods, string='Period', required=True, default='months')
    twenty4_7_hours = fields.Boolean(string='24/7')
    service_hours_from = fields.Float(string='From')
    service_hours_to = fields.Float(string='To')
    response_hours = fields.Float(string='Response Time', default=1.0)
    service_line_ids = fields.One2many('product.service.line', 'parent_id', string='Service Lines')
    warranty_contract_info = fields.Text(string='Warranty Contract Info')
    warranty_notes = fields.Text(string='Warranty Notes')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        context = self._context or {}
        service_ids = self.env['product.product'].search([('contract_ok', '=', True)])
        if context.get('contract_service'):
            contract_id = self.env['contract.contract'].browse(context.get('contract_service'))
            if contract_id:
                service_ids = [service_line.product_id.id for service_line in contract_id.service_line_ids if service_line.product_id]
                args.append(('id', 'in', service_ids))
        elif context.get('ticket_service'):
            args.append(('id', 'in', service_ids.ids))
        return super(ProductProduct, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        domain = domain or []
        context = self._context or {}
        service_ids = self.env['product.product'].search([('contract_ok', '=', True)])
        if context.get('contract_service'):
            contract_id = self.env['contract.contract'].browse(context.get('contract_service'))
            if contract_id:
                service_ids = [service_line.product_id.id for service_line in contract_id.service_line_ids if service_line.product_id]
                domain.append(('id', 'in', service_ids))
        elif context.get('ticket_service'):
            domain.append(('id', 'in', service_ids.ids))
        return super(ProductProduct, self).search_read(domain, fields, offset, limit, order)

    def open_safety_document(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_evolution.action_safety_document"
        )
        if self.safety_document_id:
            action["domain"] = [("id", "in", self.safety_document_id.ids)]
            action["views"] = [
                (
                    self.env.ref("hr_evolution.view_hr_safety_document").id,
                    "form",
                )
            ]
            action["res_id"] = self.safety_document_id.id
        return action


class ProductServiceLine(models.Model):
    _name = "product.service.line"
    _description = 'Product Service Line'

    name = fields.Char(string='Description', size=256, required=True, index=True)
    parent_id = fields.Many2one('product.product', string='Parent', ondelete='cascade', index=True)
    product_id = fields.Many2one('product.product', string='Service', required=True, index=True)
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True,
                                   default=1)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True, index=True)

    @api.onchange('product_id')
    def product_id_change(self):
        """
            Set name depends on product
        """
        self.product_uom = self.product_id.uom_id.id or False
        self.name = self.product_id.name or False
