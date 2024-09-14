from odoo import models, fields, api

class HrContractReport(models.AbstractModel):
    _name = 'report.eos_cs.report_hr_contract_end_of_service'
    _description = 'End of Service Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.contract'].browse(docids)
        return {
            'doc_ids': docids,
            'docs': docs,
        }
