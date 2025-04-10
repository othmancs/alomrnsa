# -*- coding: utf-8 -*-

from odoo import models, api

class PurchaseOrderCustomReport(models.AbstractModel):
    _name = 'report.purchase_order_report.purchase_order_custom_report'
    _description = 'Purchase Order Custom Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'o': docs[0],
            'company': docs[0].company_id,
        }