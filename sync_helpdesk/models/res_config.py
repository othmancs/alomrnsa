# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # module_sync_sale_commission = fields.Boolean(string='Sale Commission', help="""Commission""")
    module_sync_helpdesk_timesheet_invoice = fields.Boolean(string='Timesheet Invoice', help="""Timesheet Invoice.""")
    group_group_enable_due_date = fields.Boolean("Enable Due Date", implied_group='sync_helpdesk.group_enable_due_date')
    group_group_enable_ticket_priority = fields.Boolean("Enable Priority", implied_group='sync_helpdesk.group_enable_ticket_priority')
    group_group_share_ticket = fields.Boolean("Share Ticket", implied_group='sync_helpdesk.group_share_ticket')
    # module_sync_document_attachment = fields.Boolean(string='Enable Attachments', help="""Add attachments""")
    module_sync_helpdesk_dashboard = fields.Boolean(string='Dashboard', help="""Helpdesk Dashboard""")
    module_sync_helpdesk_appointment = fields.Boolean(string='Ticket Appointment', help="""Create Appointment of Ticket""")
    module_sync_helpdesk_sequence = fields.Boolean(string='Change Ticket Sequence', help="""Change Ticket sequence""")
    module_sync_helpdesk_rma = fields.Boolean(string='RMA', help="""RMA""")
    module_sync_helpdesk_merge_ticket = fields.Boolean(string='Merge Ticket', help="""Merge Ticket""")
    module_sync_helpdesk_merge_timesheet = fields.Boolean(string='Merge Ticket Timesheets', help="""Merge Ticket Timesheets""")
    # module_sales_warranty = fields.Boolean(string='Sales Warranty', help="""Sales Warranty""")
    # module_sales_warranty_sms = fields.Boolean(string='Allow Sales Warranty SMS', help="""Sales Warranty SMS""")
    module_sync_helpdesk_rma_warranty = fields.Boolean(string='RMA Warranty', help="""RMA Warranty""")
    module_sync_helpdesk_rma_sms = fields.Boolean(string='Allow RMA SMS', help="""RMA SMS""")
    sale_warranty_type = fields.Selection([('current', 'Current Warranty'), ('extend', 'Extend Warranty')], default="current", config_parameter='sync_helpdesk.sale_warranty_type')
    module_one_time_use_product = fields.Boolean(string='Enable One-Time-Use Inventory Items', help="""Enable One-Time-Use Inventory Items""")
    module_sync_helpdesk_intake = fields.Boolean(string='Enable Intake Form', help="""Enable Intake Form""")
    module_sync_helpdesk_intake_timesheet = fields.Boolean(string='Enable Intake Timesheet', help="""Enable Intake Timesheet""")
    module_sync_helpdesk_outtake = fields.Boolean(string='Enable Outtake Form', help="""Enable Outtake Form""")
    module_sync_helpdesk_automation = fields.Boolean(string='Ticket Automation', help="""Ticket Automation""")
    module_repair_purchase = fields.Boolean(string='Auto Create Repair Purchase', help="""Auto create repair purchase""")
    invoice_method = fields.Selection([
        ("b4repair", "Before Repair"),
        ("after_repair", "After Repair")], string="Invoice Method",
        default='b4repair', index=True, config_parameter='sync_helpdesk.invoice_method',
        help='Selecting \'Before Repair\' or \'After Repair\' will allow you to generate invoice before or after the repair is done respectively. \'No invoice\' means you don\'t want to generate invoice for this repair order.')
    module_sync_helpdesk_refurbs = fields.Boolean(string='Ticket Refurbs', help="""Ticket Refurbs""")
    module_sync_helpdesk_ticket_recurring = fields.Boolean(string='Recurring Tickets', help="""Recurring Tickets""")
    module_sync_helpdesk_lead = fields.Boolean(string='Create Tickets from Leads (If valid)', help="""Create Tickets from Leads (if valid)""")
    module_purchase = fields.Boolean(string='Enable Purchase Orders',
        help="""Purchase order for order parts""")
    module_sync_helpdesk_sale_quote = fields.Boolean(string='Enable Ticket Estimation',
        help="""Send Estimation to customer""")
    module_website_purchase_quote = fields.Boolean(string='Approval/Decline purchases with Digital signature',
        help="""Approval/Decline purchases with Digital signature""")
    module_sync_helpdesk_sms = fields.Boolean(string='Allow Ticket SMS',
        help="""Send SMS to customer.""")
    module_sync_helpdesk_escalation = fields.Boolean(string='Allow Escalate Ticket',
        help="""Escalate ticket to the parent team.""")
    module_sync_helpdesk_rework = fields.Boolean(string='Ticket Rework',
        help="""Rework of tickets.""")
    module_sync_helpdesk_contract = fields.Boolean(string='Contract',
        help="""Contract create for specific duration and allow to select services of contract.""")
    module_sync_helpdesk_contract_invoice = fields.Boolean(string='Contract Invoice',
        help="""Create invoice for contract servicable line.""")
    module_sync_helpdesk_sla = fields.Boolean(string='SLA Policies',
        help="""Configure SLA as per Ticket type and stage for specific duration. \n Auto assign SLA in ticket as per ticket type and stage.""")
    module_sync_helpdesk_contract_renew = fields.Boolean(string='Contract Renew',
        help="""User easily requst for renew contract.""")
    module_sync_helpdesk_timesheet = fields.Boolean(string='Timesheet on Ticket',
        help="""Users allow to put timesheet entry for ticket wise.""")
    module_sync_helpdesk_subtickets = fields.Boolean(string='Allow Sub Tickets',
        help="""Customer submit sub issue of ticket.""")
    module_sync_helpdesk_survey = fields.Boolean(string='Ratings & Survey',
        help="""Customer fill feedback about ticket.""")
    module_sync_helpdesk_website = fields.Boolean(string='Helpdesk Website',
        help="""This installs the module helpdesk Website.""")
    module_sync_helpdesk_livechat = fields.Boolean(string='Live Chat',
        help="""This installs the module live chat.""")
    module_sync_helpdesk_knowledge_base = fields.Boolean(string='Knowledge Base',
        help="""This installs the module knowledge base.""")
    module_sync_helpdesk_website_slides = fields.Boolean(string='Slides',
        help="""This installs the module website slides.""")
    module_sync_helpdesk_contract_renew = fields.Boolean(string='Contract Renew',
        help="""This installs the module contract Renew.""")
    module_sync_helpdesk_contract_sla = fields.Boolean(string='Contract SLA',
        help="""This installs the module contract SLA.""")
    module_sync_helpdesk_unassign = fields.Boolean(string='Ticket Unassign',
        help="""This installs the module contract Renew.""")
    module_sync_helpdesk_recurring_appointment = fields.Boolean(string='Recurring Appointment',
        help="""This installs the module Recurring Appointment.""")
    rma_delivery_config = fields.Selection([("delivery_order", "Delivery Order"),
                                            ("tracking_ref", "Tracking Reference")
                                            ], default="delivery_order", string="RMA Delivery Configuration", config_parameter='sync_helpdesk.rma_delivery_config')

    @api.onchange('module_sync_helpdesk_contract')
    def _onchange_module_sync_helpdesk_contract(self):
        if not self.module_sync_helpdesk_contract:
            self.update({
                'module_sync_helpdesk_contract_renew': False,
                'module_sync_helpdesk_contract_sla': False,
                'module_sync_helpdesk_contract_invoice': False,
                'module_sync_helpdesk_recurring_appointment': False
            })

    @api.onchange('module_sync_helpdesk_appointment')
    def _onchange_module_sync_helpdesk_appointment(self):
        if not self.module_sync_helpdesk_appointment:
            self.update({
                'module_sync_helpdesk_recurring_appointment': False
            })

    @api.onchange('module_sync_helpdesk_website')
    def _onchange_module_sync_helpdesk_website(self):
        if not self.module_sync_helpdesk_website:
            self.update({
                'module_sync_helpdesk_website_slides': False,
                'module_sync_helpdesk_knowledge_base': False
            })

    @api.onchange('module_sync_helpdesk_timesheet')
    def _onchange_module_sync_helpdesk_timesheet(self):
        if not self.module_sync_helpdesk_timesheet:
            self.update({
                'module_sync_helpdesk_timesheet_invoice': False,
                'module_sync_helpdesk_merge_timesheet': False,
                'module_sync_helpdesk_intake_timesheet': False
            })

    @api.onchange('module_sync_helpdesk_sla')
    def _onchange_module_sync_helpdesk_sla(self):
        if not self.module_sync_helpdesk_sla:
            self.update({
                'module_sync_helpdesk_contract_sla': False
            })

    @api.onchange('module_sync_helpdesk_intake')
    def _onchange_module_sync_helpdesk_intake(self):
        if not self.module_sync_helpdesk_intake:
            self.update({
                'module_sync_helpdesk_outtake': False,
                'module_sync_helpdesk_intake_timesheet': False
            })

    @api.onchange('module_sync_helpdesk_escalation')
    def _onchange_module_sync_helpdesk_escalation(self):
        if not self.module_sync_helpdesk_escalation:
            self.update({
                'module_sync_helpdesk_sla': False
            })

    @api.onchange('module_sync_helpdesk_rma')
    def _onchange_module_sync_helpdesk_rma(self):
        if not self.module_sync_helpdesk_rma:
            self.update({
                'module_sync_helpdesk_rma_warranty': False,
                'module_sync_helpdesk_rma_sms': False
            })

    @api.onchange('module_sync_helpdesk_merge_ticket')
    def _onchange_module_sync_helpdesk_merge_ticket(self):
        if not self.module_sync_helpdesk_merge_ticket:
            self.update({
                'module_sync_helpdesk_merge_timesheet': False
            })

    @api.onchange('module_purchase')
    def _onchange_module_purchase(self):
        if not self.module_purchase:
            self.update({
                'module_repair_purchase': False,
                'module_sync_helpdesk_refurbs': False,
                'module_website_purchase_quote': False
            })

    # @api.model
    # def get_values(self):
    #     """
    #         Override method for set ticket config values
    #     """
    #     res = super(ResConfigSettings, self).get_values()
    #     ICPSudo = self.env['ir.config_parameter'].sudo()
    #     module_obj = self.env['ir.module.module'].sudo()
    #     if module_obj.search([('name', '=', 'sync_helpdesk_rma'), ('state', '=', 'installed')], limit=1):
    #         res.update(invoice_method=ICPSudo.get_param('sync_helpdesk.invoice_method', default='b4repair'))
    #     if module_obj.search([('name', '=', 'sync_helpdesk_rma_warranty'), ('state', '=', 'installed')], limit=1):
    #         res.update(sale_warranty_type=ICPSudo.get_param('sync_helpdesk.sale_warranty_type', default='current'))
    #     return res

    # @api.multi
    # def set_values(self):
    #     """
    #         Override method for set ticket config values
    #     """
    #     super(ResConfigSettings, self).set_values()
    #     ICPSudo = self.env['ir.config_parameter'].sudo()
    #     if self.module_sync_helpdesk_rma:
    #         ICPSudo.set_param("sync_helpdesk.invoice_method", self.invoice_method)
    #     if self.module_sync_helpdesk_rma_warranty:
    #         ICPSudo.set_param("sync_helpdesk.sale_warranty_type", self.sale_warranty_type)
