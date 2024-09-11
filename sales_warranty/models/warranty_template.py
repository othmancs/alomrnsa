# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class WarrantyTemplate(models.Model):
    _name = 'warranty.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Warranty Template"

    is_renewable = fields.Boolean(string="Is Renewable?")
    active = fields.Boolean(string="Active", default=True)
    name = fields.Char(string="Name", required=True)
    warranty_months = fields.Integer(string="Term Months", required=True, default=1)
    warranty_cost = fields.Float(string="Warranty Cost", required=True)
    warranty_renew_months = fields.Integer(string="Renew Months", default=1)
    warranty_renew_cost = fields.Float(string="Renew Cost", default=10.0)
    warranty_info = fields.Text(string="Warranty Info")
    warranty_tc = fields.Text(string="Terms & Conditions")

    @api.constrains('warranty_months')
    def check_warranty_months(self):
        for rec in self:
            if rec.warranty_months <= 0:
                raise UserError(_("Term Months must be greater than 0."))

    @api.constrains('warranty_renew_months')
    def check_warranty_renew_months(self):
        for rec in self:
            if rec.is_renewable and rec.warranty_renew_months <= 0:
                raise UserError(_("Renew Months must be greater than 0."))
