from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MaterialRequest(models.Model):
    _inherit = "material.request"

    driver_id = fields.Many2one('res.partner', 'اسم السائق')
    lading_number = fields.Char('رقم بوليصة الشحن')
    note = fields.Text(string="ملاحظات", required=False, )

    def action_confirm(self):
        res = super(MaterialRequest, self).action_confirm()
        if self.request_line_ids:
            counter = 1
            for line in self.request_line_ids:
                line.write({
                    'seq': counter
                })
                counter += 1
        return res
