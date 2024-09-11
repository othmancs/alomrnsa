# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class ChangeEnddateWizard(models.TransientModel):
    _name = "change.enddate.wizard"
    _description = "Change Vacation End Date"

    new_enddate = fields.Date(string="New End Date", required=True)
    vacation_id = fields.Many2one("hr.vacation", string="Vacation")
    enddate = fields.Date(string="Current End Date")

    def action_update_enddate(self):
        self.ensure_one()
        self.vacation_id.date_to = self.new_enddate
        notes = _(
            "Kindly update/create Time off request. Vacation End date is changed to "
            + str(self.new_enddate)
        )
        self.vacation_id.message_post(message_type="email", body=notes)
