from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    certificate_for_water = fields.Date()

    rationalization_label = fields.Date()

    certificate_of_comformity = fields.Date('Certificate Of Comformity For Regulated Products')
