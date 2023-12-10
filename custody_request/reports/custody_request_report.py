from odoo import models,fields,api,_

class FinanceApprovalReport(models.AbstractModel):
    _name = 'custody.request.report'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('custody_request.report_custody')
        docargs = {
            'doc_ids': docids,
            'doc_model': report.custody.request,
            'docs': self,
        }
        return report_obj.render('custody_request.report_custody', docargs)