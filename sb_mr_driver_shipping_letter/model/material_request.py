from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MaterialRequest(models.Model):
    _inherit = "material.request"

    driver_id = fields.Many2one('res.partner', 'اسم السائق')
    lading_number = fields.Char('رقم بوليصة الشحن')
