# -*- coding: utf-8 -*-

from odoo import fields, models



class RejecteEndServiceWizard(models.TransientModel):
    _name = "reject.end_service.wizard"
    _description = "Reject End Service Wizard"

    reject_reason = fields.Text(string="Reject Reason", copy=False, required = True,)

    def action_reject_reason(self):
        end_service = self.env['hr.end.service'].browse(self._context.get('active_ids', False))
        if end_service and end_service.state != "in_progress":
            return
        reject_reason = self.reject_reason
        if end_service and end_service.reject_reason:
            reject_reason +=  "\n" + end_service.reject_reason
        return end_service.write({"reject_reason": reject_reason, "state": "rejected" })
