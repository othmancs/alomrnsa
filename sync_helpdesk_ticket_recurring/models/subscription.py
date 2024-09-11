# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from lxml import etree
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class Subscription(models.Model):
    _inherit = "subscription.subscription"

    ticket_id = fields.Many2one("ticket.ticket", string="Ticket")
    ticket_schedule_ids = fields.One2many(
        "schedule.schedule", "ticket_subscription_id", copy=False
    )

    @api.model
    def default_get(self, fields_list):
        """
        Override method for fetch default values
        """
        context = dict(self.env.context)
        model_name = self.env.ref(
            "sync_helpdesk_ticket_recurring.subscription_document_ticket0"
        )
        result = super(Subscription, self).default_get(fields_list)
        if (
            context.get("active_model") == "ticket.ticket"
            and context.get("default_model") == "ticket.ticket"
            and context.get("active_id")
        ):
            active_id = self.env["ticket.ticket"].browse(context.get("active_id"))
            if active_id.is_done or active_id.is_cancel:
                raise UserError(
                    _("You can not create recurring ticket which are closed!")
                )
            result.update(
                {
                    "doc_source": "%s,%s" % (active_id._name, str(active_id.id)),
                    "name": active_id.name,
                    "partner_id": active_id.partner_id.id,
                    "ticket_id": active_id.id,
                    "company_id": active_id.company_id.id,
                    "user_id": self.env.uid,
                }
            )
        return result

    def model_copy(self):
        """
        Override method for the add ticket logic
        """
        for subscription in self.filtered(lambda sub: sub.cron_id):
            if not subscription.doc_source.exists():
                raise UserError(
                    _(
                        "Please provide another source document.\nThis one does not exist!"
                    )
                )
            default = {}
            # if subscription.doc_source._name != 'ticket.ticket' or not subscription.ticket_id:
            # default = {'state': 'draft'}
            documents = self.env["subscription.document"].search(
                [("model.model", "=", subscription.doc_source._name)], limit=1
            )
            fieldnames = dict(
                (f.field.name, f.value == "date" and fields.Date.today() or False)
                for f in documents.field_ids
            )
            default.update(fieldnames)
            # if there was only one remaining document to generate
            # the subscription is over and we mark it as being done
            if subscription.cron_id.numbercall == 1:
                subscription.sudo().set_done()
            else:
                subscription.write({"state": "running"})
            if (
                subscription.doc_source._name == "ticket.ticket"
                and subscription.partner_id
                and subscription.ticket_id
            ):
                default.update(
                    {
                        "partner_id": subscription.partner_id.id,
                        "team_id": subscription.ticket_id.team_id.id,
                        "user_id": subscription.ticket_id.user_id.id,
                        "priority": subscription.ticket_id.priority,
                        "tag_ids": [(6, 0, subscription.ticket_id.tag_ids.ids)],
                    }
                )
                project = (
                    self.env["ir.config_parameter"]
                    .sudo()
                    .search([("key", "=", "sync_helpdesk_timesheet.ticket_project_id")])
                )
                if project:
                    default.update(
                        {
                            "project_id": subscription.ticket_id.project_id.id,
                        }
                    )

            copied_doc = subscription.doc_source.copy(default)
            if copied_doc and copied_doc._name == "ticket.ticket":
                copied_doc.onchange_stage_id()
            self.env["subscription.subscription.history"].create(
                {
                    "subscription_id": subscription.id,
                    "date": fields.Datetime.now(),
                    "document_id": "%s,%s"
                    % (subscription.doc_source._name, copied_doc.id),
                }
            )
            if (
                subscription.doc_lines
                and len(subscription.doc_lines) >= subscription.exec_init
            ):
                pass
                # subscription.sudo().set_done()
            if subscription.ticket_id:
                for doc in subscription.doc_lines:
                    for schedule in subscription.ticket_schedule_ids:
                        if schedule.date.strftime("%Y-%m-%d") == doc.date.strftime(
                            "%Y-%m-%d"
                        ):
                            schedule.update(
                                {
                                    "ticket_id": doc.document_id.id,
                                    "status": "created",
                                }
                            )

    def _recurring_ticket_schedule(self):
        for rec in self:
            schedules = []
            recent_date = rec.date_init
            if rec.ticket_id:
                for count in range(rec.exec_init):
                    vals = {
                        "date": recent_date,
                        "status": "not_created",
                        "ticket_id": rec.ticket_id.id,
                        "ticket_subscription_id": rec.id,
                    }
                    schedules += rec.ticket_schedule_ids.create(vals)
                    if rec.interval_number and rec.interval_type == "days":
                        recent_date = recent_date + relativedelta(
                            days=rec.interval_number
                        )
                    elif rec.interval_number and rec.interval_type == "weeks":
                        recent_date = recent_date + relativedelta(
                            weeks=rec.interval_number
                        )
                    elif rec.interval_number and rec.interval_type == "months":
                        recent_date = recent_date + relativedelta(
                            months=rec.interval_number
                        )

    def set_process(self):
        for subscription in self:
            subscription._recurring_ticket_schedule()
        return super(Subscription, self).set_process()

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """
        Override method for the hide create button
        """
        res = super(Subscription, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if self.env.context.get("from_ticket"):
            root = etree.fromstring(res["arch"])
            root.set("create", "false")
            res["arch"] = etree.tostring(root)
        return res


class Schedule(models.Model):
    _inherit = "schedule.schedule"

    ticket_id = fields.Many2one("ticket.ticket", string="Ticket")
    ticket_subscription_id = fields.Many2one(
        "subscription.subscription", string="Subscription"
    )
