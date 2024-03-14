# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class RejectReasonWizard(models.TransientModel):
    _name = "reject.reason.wizard"
    _description = "Material Request Reject Reason Wizard"

    reject_reason = fields.Text(string="Reject Reason", required=True)
    material_request_id = fields.Many2one("material.request", string="Material Request")

    def reject_material_req(self):
        self.material_request_id.write({"state": "reject", "delivery_state": ""})
        display_msg = (
            "<p> User %s Rejected the material request.<br/>"
            "Rejected Reason: %s </p>" % (self.env.user.name, self.reject_reason)
        )
        self.material_request_id.message_post(body=display_msg)

    @api.constrains("reject_reason")
    def check_reject_reason(self):
        if not self.reject_reason.strip():
            raise ValidationError("Please add reason description.")
