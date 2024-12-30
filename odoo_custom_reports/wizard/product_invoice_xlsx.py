# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, fields, models, _

class ProductInvoiceXlsx(models.TransientModel):
    _name = "product.invoice.xlsx"
    _description = "Product Invoice Report Xlsx"

    start_date = fields.Date(string='From Date', required='1', help='select start date')
    end_date = fields.Date(string='To Date', required='1', help='select end date')
    total_amount_due = fields.Integer(string='Total Invoice Amount')


    # Excel Report
    def check_excel_report(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date'])[0]
        return self._print_report_xlsx(data)

    def _print_report_xlsx(self, data):
        data['form'].update(self.read(['start_date', 'end_date'])[0])
        return self.env.ref('odoo_custom_reports.action_product_invoice_xlsx').report_action(self, data=data, config=False)


