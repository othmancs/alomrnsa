# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    institute = fields.Boolean('Institute', help="Check this box if this contact is a institute.")
    employee = fields.Boolean('Employee')

    def contact_individual_assign(self):
        for record in self:
            if record.email.endswith('@ewsionline.com'):
                record.company_type = 'person'


class ResCompany(models.Model):
    _inherit = 'res.company'

    company_number = fields.Char(string='Company Number')
