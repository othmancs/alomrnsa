# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import UserError


class Ticket(models.Model):
    _inherit = "ticket.ticket"
    _description = "Ticket Escalate"

    escalate = fields.Boolean("Escalate")

    def escalate_support_team(self):
        """
        Escalate ticket to the parent team
        """
        if self.team_id and not self.team_id.parent_id:
            raise UserError(
                _(
                    "Ticket is not escalate because %s team has not parent team!"
                    % (self.team_id.name)
                )
            )
        elif self.team_id:
            self.team_id = self.team_id.parent_id and self.team_id.parent_id.id
            self.user_id = self.team_id.user_id and self.team_id.user_id.id
            if not self.escalate:
                self.ticket_no = self.ticket_no + "/E"
            self.escalate = True
            try:
                template_id = self.env.ref(
                    "sync_helpdesk_escalation.ticket_assign_email"
                )
            except ValueError:
                template_id = False
            if template_id:
                template_id.send_mail(self.id, force_send=True, raise_exception=False)
        else:
            raise UserError(_("Ticket is not escalate because team is not Assign!"))
        return self.user_id.id
