# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class PrintQRLabel(models.TransientModel):
    _name = 'print.qr.label'
    _description = 'Print QR Label'

    label_size = fields.Selection([('two_by_four', '2”x4”'),
                                ('four_by_six', '4”x6”')], string='Label Size', default='two_by_four')
    product_ids = fields.Many2many('product.template', string='Products')
    
    def confirm(self):

        # self.ensure_one()
        # xml_id, data = self._prepare_report_data()
        if self.label_size == 'two_by_four':
            xml_id = 'saudi_hr_it_operations.report_product_template_qr_label_two_by_four'
        else:
            xml_id = 'saudi_hr_it_operations.report_product_template_qr_label_four_by_six'
        # if not xml_id:
        #     raise UserError(_('Unable to find report template for %s format', self.print_format))
        report_action = self.env.ref(xml_id).report_action(self.product_ids)
        report_action.update({'close_on_report_download': True})
        return report_action
        # return True

