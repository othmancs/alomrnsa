# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FinancialReportWizard(models.TransientModel):
    _name = 'financial.report.wizard'
    _description = 'Financial Report Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    branch_id = fields.Many2one('res.branch', string="Branch")
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('transfer', 'Transfer')
    ], string="Payment Type")

    def generate_report(self):
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'branch_id': self.branch_id.id if self.branch_id else False,
            'payment_type': self.payment_type
        }
        return self.env.ref('financial_report_module.financial_report_action').report_action(self, data=data)
