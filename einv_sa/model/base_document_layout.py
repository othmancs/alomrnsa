#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning


class BaseDocumentLayout(models.TransientModel):
    _name = "base.document.layout"
    _description = "einv.base_document_layout"
    _inherit = "base.document.layout"
    company_registry = fields.Char(string="CR", related='company_id.company_registry', help="")
    vat = fields.Char(related='company_id.vat', readonly=True)

    building_no = fields.Char(string="Building no", related='company_id.building_no', help="Building No")
    district = fields.Char(string="District", related='company_id.district', help="District")
    code = fields.Char(string="Code", related='company_id.code', help="Code")
    additional_no = fields.Char(string="Additional no", related='company_id.additional_no', help="Additional No")
    other_id = fields.Char(string="Other ID", related='company_id.other_id', help="")
